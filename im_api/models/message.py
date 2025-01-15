from dataclasses import dataclass
from typing import Any, Dict, Optional

from im_api.models.platform import Platform


@dataclass
class User:
    """用户信息"""
    id: str                     # 用户ID
    name: Optional[str] = None  # 用户名称
    nick: Optional[str] = None  # 用户昵称
    avatar: Optional[str] = None  # 头像URL
    is_bot: bool = False        # 是否为机器人

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=str(data.get('id')),
            name=data.get('name'),
            nick=data.get('nick'),
            avatar=data.get('avatar'),
            is_bot=data.get('is_bot', False)
        )


@dataclass
class Channel:
    """频道信息"""
    id: str                      # 频道ID
    type: str                    # 频道类型 (group/private/channel)
    name: Optional[str] = None   # 频道名称
    guild_id: Optional[str] = None  # 服务器ID（用于Discord等平台）

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Channel':
        return cls(
            id=str(data.get('id')),
            type=data.get('type', 'channel'),
            name=data.get('name'),
            guild_id=data.get('guild_id')
        )


@dataclass
class Message:
    """消息对象"""
    id: str                # 消息ID
    content: str           # 消息内容
    channel: Channel       # 频道信息
    user: User            # 发送者信息
    platform: Optional[Platform] = None  # 消息来源平台
    reply_to: Optional[str] = None  # 回复的消息ID
    created_at: Optional[str] = None  # 消息创建时间

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(
            id=data['id'],
            content=data['content'],
            channel=Channel.from_dict(data['channel']),
            user=User.from_dict(data['user']),
            platform=data.get('platform'),
            reply_to=data.get('reply_to'),
            created_at=data.get('created_at')
        )


@dataclass
class Event:
    """事件对象"""
    id: str                # 事件ID
    type: str             # 事件类型
    platform: Platform     # 事件来源平台
    channel: Optional[Channel] = None  # 相关频道
    user: Optional[User] = None       # 相关用户
    data: Dict[str, Any] = None      # 事件数据

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        return cls(
            id=data['id'],
            type=data['type'],
            platform=data['platform'],
            channel=Channel.from_dict(data['channel']) if data.get('channel') else None,
            user=User.from_dict(data['user']) if data.get('user') else None,
            data=data.get('data')
        )


# 导出
__all__ = ["User", "Channel", "Message", "Event"]

