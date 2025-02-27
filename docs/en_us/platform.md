# ImAPI Architecture Overview

## System Roles

The ImAPI architecture includes the following main roles:

1. **External Systems**: Other IM platforms supported by ImAPI that interact with MCDR, such as QQ, Kook, Discord, Telegram, etc.
2. **ImAPI**: The core plugin for event processing, responsible for unifying and processing messages and events from various platforms, and broadcasting them as standardized events
3. **Reactor**: An extensible application layer decoupled from platform protocols, responding to and processing events based on ImAPI. In terms of MCDR plugin relationships, Reactor plugins depend on ImAPI

## Plugin Tree

```mermaid
graph TD
%%MCDR
mcdr[Mcdreforged]
%%im-api
subgraph api[ImAPI]
core
subgraph drivers
qq[QQDriver]
kook[KookDriver]
tg[TelegramDriver]
other[...]
end
end
%%satori-sub-plugin
subgraph sub-plugin
subgraph reactor
qq_chat[QQChat]
kookin[KookIn]
other2[...]
end
end

api --register plugin--> mcdr
other2 -.-> api
qq_chat -.-> api
kookin -.-> api
sub-plugin --register plugin--> mcdr
```

## Core Components

### ImAPI Core

The core components of ImAPI include:

1. **MCDREntry**: Plugin entry point, responsible for initializing and managing ImAPI's lifecycle
2. **DriverManager**: Driver manager, responsible for managing driver instances for various platforms
3. **EventProcessor**: Event processor, handles messages and events from various platforms
4. **MessageBridge**: Message bridge, responsible for forwarding messages between different platforms

### ImAPI Driver

The driver layer implements specific communication with various platforms:

1. **QQDriver**: QQ platform driver
2. **KookDriver**: Kook platform driver
3. **TelegramDriver**: Telegram platform driver
4. **SatoriDriver**: Satori protocol driver

## Registration and Loading Process

### Overview

1. When ImAPI loads, it starts corresponding receivers based on the configuration file
2. When Reactor loads, it sends a register event to MCDR, and ImAPI listens to this event to add the corresponding plugin to the registry

### Loading Flow Chart

```mermaid
sequenceDiagram
actor player as Player
participant mcdr as MCDReforged
participant api as ImAPI
participant rtr as Reactor
actor plat as Platform

player ->>+ mcdr: start/reload im_api
mcdr ->>+ api: load plugin
api ->> api: load drivers
api -->- mcdr: load finish

mcdr ->>+ rtr: load receiver
rtr -->>- mcdr: load finish
mcdr -->>- player: start/reload im_api finish

plat ->> api: msg/event from platform
api ->> api: process msg/event
api -) mcdr: send [im_api] event
mcdr  -) rtr: forward [im_api] event
rtr ->> rtr: process im_api event
rtr ->> plat: [optional] reply event
rtr ->> mcdr: [optional] operate mc server
```

### Component Relationship Diagram

```mermaid
flowchart LR
    subgraph ImAPI
        entry[MCDREntry]
        subgraph ImAPI-Core
            driver[DriverManager]
            ep[EventProcessor]
            message_bridge[MessageBridge]
        end
        subgraph ImAPI-Driver
            qq[QQDriver]
            kook[KookDriver]
            tg[TelegramDriver]
            satori[SatoriDriver]
            other[...]
        end
    end
```