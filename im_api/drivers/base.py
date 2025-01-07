from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Union

from im_api.core.context import Context
from im_api.models.parser import Event, Message
from im_api.models.request import SendMessageRequest
from im_api.models.platform import Platform

class BaseDriver(ABC):
    """驱动基类，定义了驱动的基本接口"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化驱动"""
        self.config = config
        self.connected = False
        self.message_callback: Optional[Callable[[str, Message], None]] = None
        self.event_callback: Optional[Callable[[str, Event], None]] = None
        self.logger = Context.get_instance().logger
        
    @abstractmethod
    def connect(self) -> None:
        """连接到平台"""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """断开与平台的连接"""
        pass
        
    @abstractmethod
    def send_message(self, request: SendMessageRequest) -> Optional[str]:
        """发送消息
        
        Args:
            request: 发送消息请求
            
        Returns:
            消息ID, 如果发送失败则返回 None
        """
        pass
        
    def register_callbacks(self, message_callback: Callable[[str, Message], None], event_callback: Callable[[str, Event], None]):
        """注册回调函数"""
        self.message_callback = message_callback
        self.event_callback = event_callback
        self.logger.debug(f"Registered callbacks for {self.get_platform()} driver")

    @classmethod
    def get_platform(cls) -> Union[Platform, str]:
        """Return the platform identifier"""
        raise NotImplementedError()

# 导出
__all__ = ["Platform", "BaseDriver"]
