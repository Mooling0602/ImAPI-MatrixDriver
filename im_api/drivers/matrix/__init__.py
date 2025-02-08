import asyncio

from typing import Optional
from nio import AsyncClient, SyncError, UploadFilterError , RoomMessageText, RoomSendResponse
from mcdreforged.api.decorator import new_thread

from im_api.models.request import SendMessageRequest
from im_api.models.platform import Platform
from im_api.drivers import BaseDriver
from im_api.config import MatrixConfig

from .resp import textmsg_callback, on_sync_error

class MatrixDriver(BaseDriver):
    """
    Matrix 驱动实现
    注意：你需要预先获取一个活跃且可用的会话token，且此token需要和你的机器人账号的user_id严格对应，可以尝试使用MatrixSync-MCDR项目
    """

    @classmethod
    def get_platform(cls) -> Platform:
        return Platform.MATRIX
    
    def __init__(self, config: MatrixConfig):
        """初始化驱动"""
        self.user_id = config.user_id
        self.token = config.token
        self.homeserver = config.homeserver
        self.client = AsyncClient(homeserver=self.homeserver, device_id='mcdr')
        self.client.user_id = self.user_id
        self.client.access_token = self.token
        self.receiver = None

        self.logger.info(f"Initializing matrix driver with connection_type={self.connection_type}")
        
    def connect(self) -> None:
        """和Matrix平台同步各种事件"""
        if self.connected:
            return

        async def receive_messages() -> None:
            client = self.client

            # 响应同步错误
            client.add_response_callback(on_sync_error, SyncError)
            filter_data = {"timeline": {"not_senders": [client.user_id]}}
            filter_resp = await client.upload_filter(room=filter_data)
            if isinstance(filter_resp, UploadFilterError):
                self.logger.error(filter_resp)
            import im_api.drivers.matrix.resp as resp
            if resp.homeserver_online:
                await client.sync()
                client.add_event_callback(textmsg_callback, RoomMessageText)
                try:
                    self.receiver = asyncio.create_task(client.sync_forever(sync_filter=resp.filter_id))
                except asyncio.CancelledError:
                    self.logger.warning('Receiver task has been cancelled!')
                except Exception as e:
                    self.logger.error(f"Receiver sync error: {e}", "Receiver")
                    self.receiver.cancel()
                finally:
                    if self.receiver:
                        self.receiver.cancel()
                    if client is not None:
                        await client.close
            
        async def add_sync_task():
            await receive_messages()

        @new_thread('ImAPI: MatrixReceiver')
        def run_sync_task():
            asyncio.run(add_sync_task())

        run_sync_task()
        self.connected = True
        
    def disconnect(self) -> None:
        """断开与Matrix平台的连接"""
        if not self.connected:
            return

        if isinstance(self.receiver, asyncio.Task):
            self.receiver.cancel()
        
    def send_message(self, request: SendMessageRequest) -> Optional[str]:
        """发送消息
        
        Args:
            request: 发送消息请求
            
        Returns:
            消息ID, 如果发送失败则返回 None
        """
        if not self.connected:
            self.logger.error("Cannot send message: driver not connected")
            return None
        async def _send_message():
            client = self.client
            return await client.room_send(
                room_id=request.channel_id,
                message_type="m.room.message",
                content={"msgtype": "m.text", "body": request.content},
            )
        try:
            future = asyncio.run_coroutine_threadsafe(_send_message(), self.event_loop)
            # 最多等待5s
            result = future.result(timeout=5)
            if isinstance(result, RoomSendResponse):
                return str(result.event_id)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return None

# 导出
__all__ = ["Platform", "MatrixDriver"]