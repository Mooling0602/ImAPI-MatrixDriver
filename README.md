![ImAPI](https://socialify.git.ci/MCDReforged-Towhee-Community/ImAPI/image?description=1&font=Inter&forks=1&issues=1&language=1&name=1&owner=1&pattern=Plus&pulls=1&stargazers=1&theme=Auto)

## 概要说明
以ImAPI作为核心插件的架构，主要有如下几个角色

1. **外部系统**: 与MCDR互通且ImAPI支持的其他im平台，例如QQ，Kook，Discord，Telegram等
2. **ImAPI**: 事件处理的核心插件，负责将所有来自各个平台的消息与事件做统一处理，并封装成统一格式的事件(Event)进行广播
3. **Reactor**: 可扩展的、与平台协议解耦的应用层，基于ImAPI的事件进行响应与处理。在MCDR的插件关系上，Reactor插件依赖ImAPI

## 插件事件

`ImAPI`针对各外部系统的消息与事件进行了统一封装，封装后的事件类型为`Message`和`Event`。在`ImAPI`处理完消息与事件后，会将其封装成`Message`或`Event`并通过[MCDR自定义事件](https://docs.mcdreforged.com/zh-cn/latest/plugin_dev/event.html#default-event-listener)进行广播。下游的`Reactor`插件应当订阅相应的事件实现自己的功能和逻辑。

下游如果想和平台交互，可以通过发送`ImAPI`订阅的事件到`MCDR`以通过`ImAPI`向平台发送消息或者进行操作。

### 能力支持

|事件\平台|QQ|Telegram|Discord|Kook|Matrix|
|:-:|:-:|:-:|:-:|:-:|:-:|
|接收私聊消息|✅|✅||||
|发送私聊消息|✅|✅||||
|接收群聊消息|✅|✅||||
|接收群聊消息|✅|✅||||
|加入群聊通知|✅|✅||||
|退出群聊通知|✅|✅||||

### 平台消息(im_api.message)
```python
from mcdreforged.api.all import *
from im_api.drivers.base import Platform
from im_api.models.message import Event, Message

server.register_event_listener("im_api.message", on_message)

def on_message(message: Message):
    server.logger.info(f"Received message: {message.content}")
```
### 平台事件(im_api.event)
```python
from mcdreforged.api.all import *
from im_api.drivers.base import Platform
from im_api.models.message import Event, Message

server.register_event_listener("im_api.event", on_event)

def on_event(message: Message):
    server.logger.info(f"Received event: {message.event}")
```
### 向平台发送消息(im_api.send_message)
```python
from im_api.models.request import MessageType, SendMessageRequest, ChannelInfo
from mcdreforged.api.all import *

def send_msg_to_qq():
    request = SendMessageRequest(
        platforms=[Platform.QQ],
        channel=ChannelInfo(id='114514', type=MessageType.PRIVATE),
        content='Hello, MCDR!'
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))
```



## License

Copyright © 2025 [MCDReforged-Towhee-Community](https://github.com/MCDReforged-Towhee-Community) and Contributors

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

本程序是自由软件：你可以再分发之和/或依照由自由软件基金会发布的 GNU 通用公共许可证修改之，无论是版本 3 许可证，还是（按你的决定）任何以后版都可以。
