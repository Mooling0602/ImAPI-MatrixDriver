# Plugin Development Guide

This document will guide you on how to develop downstream plugins using ImAPI, including common features like event listening and message sending.

## Event Listening

### Listening to Message Events

You can handle messages from various platforms by registering event listeners:

```python
from mcdreforged.api.all import *
from im_api.models.message import Message

def on_load(server: PluginServerInterface, old):
    server.register_event_listener("im_api.message", on_message)

def on_message(message: Message):
    # Message event handling
    server.logger.info(f"Received message: {message.content}")
    server.logger.info(f"From platform: {message.platform}")
    server.logger.info(f"Sender: {message.sender}")
```

### Listening to Other Events

Besides message events, you can listen to other types of events:

```python
from mcdreforged.api.all import *
from im_api.models.message import Message

def on_load(server: PluginServerInterface, old):
    server.register_event_listener("im_api.event", on_event)

def on_event(message: Message):
    server.logger.info(f"Received event: {message.event}")
```

## Sending Messages

### Sending Private Messages

Use the `im_api.send_message` event to send private messages:

```python
from mcdreforged.api.all import *
from im_api.models.request import MessageType, SendMessageRequest, ChannelInfo
from im_api.models.platform import Platform

def send_private_message():
    request = SendMessageRequest(
        platforms=[Platform.QQ],  # Specify target platform
        channel=ChannelInfo(id='114514', type=MessageType.PRIVATE),  # Private chat target
        content='Hello, MCDR!'  # Message content
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))
```

### Sending Group Messages

Sending group messages is similar to private messages, just change the `channel` type:

```python
from mcdreforged.api.all import *
from im_api.models.request import MessageType, SendMessageRequest, ChannelInfo
from im_api.models.platform import Platform

def send_group_message():
    request = SendMessageRequest(
        platforms=[Platform.QQ],
        channel=ChannelInfo(id='114514', type=MessageType.GROUP),  # Group chat target
        content='Hello, Group!'
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))
```

### Multi-Platform Sending

You can send messages to multiple platforms simultaneously:

```python
from mcdreforged.api.all import *
from im_api.models.request import MessageType, SendMessageRequest, ChannelInfo
from im_api.models.platform import Platform

def send_multi_platform():
    request = SendMessageRequest(
        platforms=[Platform.QQ, Platform.TELEGRAM],  # Specify multiple platforms
        channel=ChannelInfo(id='114514', type=MessageType.GROUP),
        content='Hello, Everyone!'
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))
```

## Best Practices

1. Always use type annotations for better code hints
2. Use exception handling to catch potential sending failures
3. Choose appropriate message types based on actual needs
4. Use logging reasonably to record message processing

## API Reference

### Message Class

Message objects contain the following main attributes:

- `platform`: Message source platform
- `channel`: Message channel information
- `sender`: Sender information
- `content`: Message content
- `event`: Event type (if it's an event message)

### SendMessageRequest Class

Send message requests contain the following main parameters:

- `platforms`: Target platform list
- `channel`: Target channel information
- `content`: Message content to send