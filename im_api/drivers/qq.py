import asyncio
import json
import threading
from typing import Any, Optional, Literal

from aiohttp import web, ClientSession, ClientWebSocketResponse
from aiocqhttp import CQHttp, Event as CQEvent
from mcdreforged.api.all import *

from im_api.config import ConnectionType, QQConfig, WsClientConfig, WSServerConfig
from im_api.drivers.base import BaseDriver, Platform
from im_api.models.message import Message, Event, User, Channel
from im_api.models.request import SendMessageRequest, MessageType


class QQDriver(BaseDriver):
    """QQ 驱动实现，支持正向和反向 WebSocket 连接"""
    
    @classmethod
    def get_platform(cls) -> Platform:
        return Platform.QQ
    
    def __init__(self, config: QQConfig):
        super().__init__(config)
        self.connection_type = config.connection_type
        
        if self.connection_type == ConnectionType.WS_SERVER:
            self.host = config.server.host
            self.port = config.server.port
            self.access_token = config.server.access_token
            self.url_prefix = config.server.url_prefix  # 移除末尾的斜杠
        else:
            self.ws_url = config.client.ws_url
            self.access_token = config.client.access_token
            self.heartbeat = config.client.heartbeat
        
        self.logger.info(f"Initializing QQ driver with connection_type={self.connection_type}")
        
        # 创建 bot 实例
        self.bot = CQHttp(
            api_root=None,  # 不使用 HTTP API
            access_token=self.access_token
        )
        self.event_loop = None
        self.server_thread = None
        
        # 反向 WebSocket 相关
        self.app = web.Application()
        self.runner = None
        self.site = None
        
        # 正向 WebSocket 相关
        self.ws_client: Optional[ClientWebSocketResponse] = None
        self.client_session: Optional[ClientSession] = None
        self.reconnect_task = None
        self.ws_heartbeat_task = None
        
        self.startup_event = threading.Event()
        self.ws_connections = {}  # 存储所有 WebSocket 连接及其锁
        self.ws_locks = {}  # WebSocket 连接的锁

        # 注册事件处理器
        @self.bot.on_message
        async def handle_msg(event: CQEvent):
            self.logger.debug(f"Received message: {event.message} from {event.user_id}")
            # 转换为 Satori 消息格式
            message = Message(
                id=str(event.message_id),
                content=event.message,
                channel=Channel(
                    id=str(event.group_id) if event.group_id else str(event.user_id),
                    type="group" if event.group_id else "private",
                    name=event.group_name if hasattr(event, 'group_name') else None
                ),
                user=User(
                    id=str(event.user_id),
                    name=event.sender.get("nickname", ""),
                    avatar=f"http://q1.qlogo.cn/g?b=qq&nk={event.user_id}&s=640"
                ),
                platform=Platform.QQ
            )
            self.logger.debug(f"Received message: {message.content} from {message.user.id} in {message.channel.id}")
            # 触发消息事件
            if self.message_callback:
                self.message_callback(Platform.QQ, message)
                self.logger.debug("Message forwarded to MCDR")
            else:
                self.logger.warning("No message callback registered")
            
        @self.bot.on_notice
        async def handle_notice(event: CQEvent):
            self.logger.info(f"Received notice: {event.notice_type} from {event.user_id}")
            # 转换为 Satori 事件格式
            if event.notice_type == "group_increase":
                evt = Event(
                    id=str(event.time),
                    type="guild.member.join",
                    platform=Platform.QQ,
                    channel=Channel(
                        id=str(event.group_id),
                        type="group"
                    ),
                    user=User(
                        id=str(event.user_id)
                    )
                )
            elif event.notice_type == "group_decrease":
                evt = Event(
                    id=str(event.time),
                    type="guild.member.leave",
                    platform=Platform.QQ,
                    channel=Channel(
                        id=str(event.group_id),
                        type="group"
                    ),
                    user=User(
                        id=str(event.user_id)
                    )
                )
            else:
                self.logger.debug(f"Ignoring unsupported notice type: {event.notice_type}")
                return
                
            # 触发事件
            if self.event_callback:
                self.logger.debug(f"Forwarding event to MCDR: {evt}")
                self.event_callback(Platform.QQ, evt)
            else:
                self.logger.warning("No event callback registered")
            
        async def handle_ws(request):
            """处理 WebSocket 连接"""
            self.logger.info("New WebSocket connection")
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            
            # 为新连接创建锁
            ws_id = id(ws)
            self.ws_connections[ws_id] = ws
            self.ws_locks[ws_id] = asyncio.Lock()
            
            try:
                async for msg in ws:
                    if msg.type == web.WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            # 忽略心跳消息和响应消息
                            if data.get("meta_event_type") == "lifecycle" or \
                               data.get("meta_event_type") == "heartbeat" or \
                               data.get("status") == "ok":  # 忽略响应消息
                                continue
                                
                            self.logger.info(f"Received WebSocket message: {data}")
                            # 创建事件对象并处理
                            event = CQEvent.from_payload(data)
                            if event.type == "message":
                                await handle_msg(event)
                            elif event.type == "notice":
                                await handle_notice(event)
                        except Exception as e:
                            self.logger.error(f"Error handling WebSocket message: {e}")
                    elif msg.type == web.WSMsgType.ERROR:
                        self.logger.error(f"WebSocket connection closed with exception {ws.exception()}")
            finally:
                # 清理连接和锁
                del self.ws_connections[ws_id]
                del self.ws_locks[ws_id]
                self.logger.info("WebSocket connection closed")
                return ws
            
        # 只在初始化时注册一次路由
        self.app.router.add_get(f"{self.url_prefix}", handle_ws)  # 使用配置的URL前缀
            
    def connect(self) -> None:
        """连接到平台"""
        if self.connected:
            self.logger.info("Already connected")
            return

        async def start():
            try:
                if self.connection_type == ConnectionType.WS_SERVER:
                    await self.start_ws_server()
                else:
                    await self.start_ws_client()
                self.startup_event.set()
            except Exception as e:
                self.logger.error(f"Failed to start {self.connection_type} WebSocket: {e}")
                self.startup_event.set()

        def run_server():
            try:
                self.event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.event_loop)
                self.event_loop.run_until_complete(start())
                self.event_loop.run_forever()
            except Exception as e:
                self.logger.error(f"Error in server thread: {e}")
                self.startup_event.set()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        self.startup_event.wait(timeout=5)
        if (self.connection_type == ConnectionType.WS_SERVER and self.site is not None) or \
           (self.connection_type == ConnectionType.WS_CLIENT and self.ws_client is not None):
            self.connected = True
            self.logger.info(f"QQ driver connected successfully using {self.connection_type} WebSocket")
        else:
            self.logger.error(f"Failed to connect QQ driver: {self.connection_type} WebSocket not started")

    async def cleanup(self):
        """清理资源"""
        if self.connection_type == ConnectionType.WS_SERVER:
            try:
                # 关闭所有 WebSocket 连接
                for ws in set(self.ws_connections.values()):
                    try:
                        await asyncio.wait_for(ws.close(code=1000, message='Server shutdown'), timeout=0.5)
                    except asyncio.TimeoutError:
                        self.logger.warning("WebSocket close timeout")
                    except Exception as e:
                        self.logger.error(f"Error closing WebSocket: {e}")
                
                # 停止站点
                if self.site:
                    await self.site.stop()
                # 清理运行器
                if self.runner:
                    await self.runner.cleanup()
            except Exception as e:
                self.logger.error(f"Error during server cleanup: {e}")
        else:
            try:
                # 取消重连任务
                if self.reconnect_task:
                    self.reconnect_task.cancel()
                # 关闭客户端连接
                if self.ws_client:
                    await self.ws_client.close()
                # 关闭会话
                if self.client_session:
                    await self.client_session.close()
            except Exception as e:
                self.logger.error(f"Error during client cleanup: {e}")

    def disconnect(self) -> None:
        """断开连接"""
        if not self.connected:
            return
            
        self.logger.info("Disconnecting QQ driver...")
        if self.event_loop:
            try:
                future = asyncio.run_coroutine_threadsafe(self.cleanup(), self.event_loop)
                future.result(timeout=2)
                self.event_loop.call_soon_threadsafe(self.event_loop.stop)
                
                if self.server_thread and self.server_thread.is_alive():
                    self.server_thread.join(timeout=2)
                    
                try:
                    self.event_loop.close()
                except:
                    pass
                    
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")
            
        self.connected = False
        self.event_loop = None
        self.server_thread = None
        self.site = None
        self.runner = None
        self.ws_client = None
        self.client_session = None
        self.app = web.Application()
        self.logger.info("QQ driver disconnected")

    async def send_ws_message(self, data: dict) -> bool:
        """发送 WebSocket 消息"""
        if self.connection_type == ConnectionType.WS_SERVER:
            # 使用反向 WebSocket 发送消息
            for ws_id, ws in list(self.ws_connections.items()):
                if ws.closed:
                    continue
                try:
                    async with self.ws_locks[ws_id]:
                        await ws.send_json(data)
                        return True
                except Exception as e:
                    self.logger.error(f"Error in WebSocket communication: {e}")
                    continue
            self.logger.warning("No active WebSocket connections")
            return False
        else:
            # 使用正向 WebSocket 发送消息
            if not self.ws_client or self.ws_client.closed:
                self.logger.error("WebSocket client not connected")
                return False
            try:
                await self.ws_client.send_json(data)
                return True
            except Exception as e:
                self.logger.error(f"Error sending message: {e}")
                return False

    def send_message(self, request: SendMessageRequest) -> Optional[str]:
        """发送消息
        
        Args:
            request: 发送消息请求
            
        Returns:
            消息ID, 如果发送失败则返回 None
        """
        # 检查是否需要处理这个请求
        if request.platforms is not None and Platform.QQ not in request.platforms:
            return None

        if not self.connected or not self.event_loop:
            self.logger.error("Cannot send message: driver not connected")
            return None
            
        # 构造消息
        message_type = "private" if request.channel.type == MessageType.PRIVATE else "group"
        action = "send_group_msg" if message_type == "group" else "send_private_msg"
        
        data = {
            "action": action,
            "params": {
                "message": request.content,
                "group_id" if message_type == "group" else "user_id": int(request.channel_id)
            }
        }

        # 处理QQ特定的参数
        if request.extra and hasattr(request.extra, 'at_sender'):
            data["params"]["at_sender"] = request.extra.at_sender
        if request.extra and hasattr(request.extra, 'auto_escape'):
            data["params"]["auto_escape"] = request.extra.auto_escape
        
        async def _send():
            success = await self.send_ws_message(data)
            return "success" if success else None
            
        future = asyncio.run_coroutine_threadsafe(_send(), self.event_loop)
        try:
            return future.result(timeout=5)
        except Exception as e:
            self.logger.error(f"Error waiting for message result: {e}")
            return None

    async def start_ws_server(self):
        """启动反向 WebSocket 服务器"""
        self.logger.info("Starting WebSocket server...")
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            self.logger.info(f"WebSocket server started at ws://{self.host}:{self.port}{self.url_prefix}")
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            raise

    async def start_ws_client(self):
        """启动正向 WebSocket 客户端"""
        self.logger.info("Starting WebSocket client...")
        self.client_session = ClientSession()
        
        async def connect_ws():
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else None
                self.ws_client = await self.client_session.ws_connect(
                    self.ws_url,
                    headers=headers,
                    heartbeat=self.heartbeat
                )
                self.logger.info(f"Connected to WebSocket server at {self.ws_url}")
                
                async for msg in self.ws_client:
                    if msg.type == web.WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            # 忽略心跳消息和响应消息
                            if data.get("meta_event_type") in ["lifecycle", "heartbeat"] or \
                               data.get("status") == "ok":
                                continue
                                
                            self.logger.debug(f"Received WebSocket message: {data}")
                            # 创建事件对象并处理
                            event = CQEvent.from_payload(data)
                            if event.type == "message":
                                await handle_msg(event)
                            elif event.type == "notice":
                                await handle_notice(event)
                        except Exception as e:
                            self.logger.error(f"Error handling WebSocket message: {e}")
                    elif msg.type in [web.WSMsgType.CLOSED, web.WSMsgType.ERROR]:
                        break
            except Exception as e:
                self.logger.error(f"WebSocket connection error: {e}")
                return False
            return True

        # 启动重连任务
        async def reconnect_loop():
            while True:
                if not self.ws_client or self.ws_client.closed:
                    self.logger.info("Attempting to connect to WebSocket server...")
                    if await connect_ws():
                        return  # 连接成功后退出循环
                    await asyncio.sleep(5)  # 重连延迟
                await asyncio.sleep(1)

        # 等待连接建立
        try:
            await reconnect_loop()
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket client: {e}")
            raise

# 导出
__all__ = ["QQDriver"] 