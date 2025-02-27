# 插件开发指南

本文档将指导您如何使用 ImAPI 开发下游插件，包括事件监听和消息发送等常见功能的实现。

## 事件监听

### 监听消息事件

您可以通过注册事件监听器来处理来自各个平台的消息：

```python
from mcdreforged.api.all import *
from im_api.models.message import Message

def on_load(server: PluginServerInterface, old):
    server.register_event_listener("im_api.message", on_message)

def on_message(message: Message):
    # 消息事件处理
    server.logger.info(f"收到消息：{message.content}")
    server.logger.info(f"来自平台：{message.platform}")
    server.logger.info(f"发送者：{message.sender}")
```

### 监听其他事件

除了消息事件，您还可以监听其他类型的事件：

```python
from mcdreforged.api.all import *
from im_api.models.message import Message

def on_load(server: PluginServerInterface, old):
    server.register_event_listener("im_api.event", on_event)

def on_event(message: Message):
    server.logger.info(f"收到事件：{message.event}")
```

## 发送消息

### 发送私聊消息

使用 `im_api.send_message` 事件发送私聊消息：

```python
from mcdreforged.api.all import *
from im_api.models.request import MessageType, SendMessageRequest, ChannelInfo
from im_api.models.platform import Platform

def send_private_message():
    request = SendMessageRequest(
        platforms=[Platform.QQ],  # 指定发送平台
        channel=ChannelInfo(id='114514', type=MessageType.PRIVATE),  # 私聊目标
        content='Hello, MCDR!'  # 消息内容
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))
```

### 发送群聊消息

发送群聊消息与私聊类似，只需修改 `channel` 的类型：

```python
from mcdreforged.api.all import *
from im_api.models.request import MessageType, SendMessageRequest, ChannelInfo
from im_api.models.platform import Platform

def send_group_message():
    request = SendMessageRequest(
        platforms=[Platform.QQ],
        channel=ChannelInfo(id='114514', type=MessageType.GROUP),  # 群聊目标
        content='Hello, Group!'
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))
```

### 多平台发送

您可以同时向多个平台发送消息：

```python
from mcdreforged.api.all import *
from im_api.models.request import MessageType, SendMessageRequest, ChannelInfo
from im_api.models.platform import Platform

def send_multi_platform():
    request = SendMessageRequest(
        platforms=[Platform.QQ, Platform.TELEGRAM],  # 指定多个平台
        channel=ChannelInfo(id='114514', type=MessageType.GROUP),
        content='Hello, Everyone!'
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))
```

## 最佳实践

1. 始终使用类型注解以获得更好的代码提示
2. 使用异常处理来捕获可能的发送失败
3. 根据实际需求选择合适的消息类型
4. 合理使用日志记录消息处理过程

## API 参考

### Message 类

消息对象包含以下主要属性：

- `platform`: 消息来源平台
- `channel`: 消息通道信息
- `sender`: 发送者信息
- `content`: 消息内容
- `event`: 事件类型（如果是事件消息）

### SendMessageRequest 类

发送消息请求包含以下主要参数：

- `platforms`: 目标平台列表
- `channel`: 目标通道信息
- `content`: 要发送的消息内容