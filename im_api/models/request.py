from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Set

from im_api.models.platform import Platform


class MessageType(Enum):
    """消息类型"""
    CHANNEL = "channel"    # 频道消息（包括QQ群、Discord频道等）
    PRIVATE = "private"    # 私聊消息
    GUILD = "guild"        # 服务器全局消息


@dataclass
class MessageExtra:
    """消息额外参数基类"""
    pass


@dataclass
class ChannelInfo:
    """频道信息"""
    id: str               # 频道ID
    type: MessageType     # 频道类型
    guild_id: Optional[str] = None  # 服务器ID（用于Discord等平台）


@dataclass
class SendMessageRequest:
    """消息发送请求"""
    channel: ChannelInfo                  # 频道信息
    content: str                          # 消息内容
    platforms: Optional[Set[Union[Platform, str]]] = None  # 目标平台列表，None表示所有平台
    extra: Optional[MessageExtra] = None  # 平台特定的额外参数
    raw_extra: Dict[str, Any] = field(default_factory=dict)  # 原始额外参数

    @property
    def channel_id(self) -> str:
        """获取频道ID"""
        return self.channel.id


# QQ平台特定的额外参数
@dataclass
class QQMessageExtra(MessageExtra):
    """QQ消息额外参数"""
    at_sender: bool = False          # 是否at发送者
    auto_escape: bool = False        # 是否转义CQ码
    user_id: Optional[int] = None    # QQ号（私聊消息）


# KOOK平台特定的额外参数
@dataclass
class KookMessageExtra(MessageExtra):
    """KOOK消息额外参数"""
    card: bool = False           # 是否为卡片消息
    quote: Optional[str] = None  # 引用消息ID


# Discord平台特定的额外参数
@dataclass
class DiscordMessageExtra(MessageExtra):
    """Discord消息额外参数"""
    embed: bool = False          # 是否为嵌入消息
    reference: Optional[str] = None  # 回复消息ID


# 导出
__all__ = ["MessageType", "MessageExtra", "QQMessageExtra", "ChannelInfo", "SendMessageRequest"]