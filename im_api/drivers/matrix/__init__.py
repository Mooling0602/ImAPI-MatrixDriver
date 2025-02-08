import asyncio

from typing import Optional
from nio import AsyncClient, SyncError, SyncResponse, UploadFilterError, UploadFilterResponse, RoomMessageText, RoomSendResponse
from mcdreforged.api.decorator import new_thread

from im_api.models.request import SendMessageRequest
from im_api.models.platform import Platform
from im_api.drivers import BaseDriver
from im_api.config import MatrixConfig

from .resp import textmsg_callback, on_sync_error, on_sync_response

receiver = None

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
        super().__init__(config)
        self.user_id = config.user_id
        self.token = config.token
        self.homeserver = config.homeserver
        self.logger.info(f"Debug: {self.homeserver}")
        self.client = AsyncClient(homeserver=self.homeserver)
        self.client.user_id = self.user_id
        self.client.access_token = self.token
        self.client.device_id = 'mcdr'

        self.logger.info(f"Initializing matrix driver...")
        
    def connect(self) -> None:
        """和Matrix平台同步各种事件"""
        if self.connected:
            return

        async def receive_messages() -> None:
            self.client.add_response_callback(on_sync_response, SyncResponse)
            self.client.add_response_callback(on_sync_error, SyncError)
            import im_api.drivers.matrix.resp as resp
            if resp.homeserver_online:
                # await self.client.sync()
                self.client.add_event_callback(textmsg_callback, RoomMessageText)
                global receiver
                self.logger.info("Creating receiver task...")
                receiver = asyncio.create_task(self.client.sync_forever(timeout=30000))
                # try:
                #     await self.client.sync(timeout=5)
                #     self.client.add_event_callback(textmsg_callback, RoomMessageText)
                #     self.receiver = asyncio.create_task(self.client.sync_forever(timeout=5))
                # except asyncio.CancelledError:
                #     self.logger.warning('Receiver task has been cancelled!')
                # except Exception as e:
                #     self.logger.error(f"Receiver sync error: {e}", "Receiver")
                #     if isinstance(self.receiver, asyncio.Task):
                #         self.logger.error("Cancelling receiver task...")
                #         self.receiver.cancel()
                # finally:
                #     if isinstance(self.receiver, asyncio.Task):
                #         self.logger.error("Cancelling receiver task...")
                #         self.receiver.cancel()
                #     if self.client is not None:
                #         self.logger.error("Cancelling receiver client...")
                #         await self.client.close()
            
        async def add_sync_task():
            self.logger.info("Starting event loop...")
            await receive_messages()

        @new_thread('ImAPI: MatrixReceiver')
        def run_sync_task():
            self.logger.info("Starting receiver task...")
            asyncio.run(add_sync_task())

        run_sync_task()
        self.connected = True
        
    def disconnect(self) -> None:
        """断开与Matrix平台的连接"""
        if not self.connected:
            return

        if isinstance(receiver, asyncio.Task):
            receiver.cancel()
            self.connected = False
        
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