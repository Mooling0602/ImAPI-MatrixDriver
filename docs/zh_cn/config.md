# 配置指南

本文档将指导您如何配置 ImAPI，包括默认配置文件的结构说明、各个配置项的详细解释，以及不同平台的具体配置方法。

## 配置文件结构

ImAPI 使用 YAML 格式的配置文件。MCDR 会在首次加载im_api时初始化该配置文件到`config/im_api/config.yml`，您需要在首次加载后对配置文件进行修改才能正常工作。

以下是配置文件的基本结构：

```yaml
drivers:
  # QQ 驱动配置
  - enabled: true
    platform: qq
    # 连接类型: ws_server(Onebot反向WS) 或 ws_client(Onebot正向WS)
    connection_type: ws_server
    # 反向 WebSocket 配置 (connection_type 为 ws_server 时使用)
    ws_server:
      host: 0.0.0.0
      port: 8080
      access_token: ""   # 访问令牌，留空则不验证
      url_prefix: /ws/   # WebSocket URL前缀
    
    # 正向 WebSocket 配置 (connection_type 为 ws_client 时使用)
    ws_client:
      ws_url: ws://127.0.0.1:6700
      access_token: ""   # 访问令牌，留空则不验证
      heartbeat: 30  # 心跳间隔（秒）
  
  # Telegram 驱动配置
  - enabled: false
    platform: telegram
    token: ""
    http_proxy: ""

  # Matrix 驱动配置
  - enabled: false
    platform: matrix
    account:
      user_id: ""
      token: ""
    homeserver: "example.com"
```

## 配置项说明

### QQ 平台配置

- `enabled`: 是否启用 QQ 平台
- `platform`: 平台标识符，固定为 "qq"
- `connection_type`: 连接类型(注：此处是`im_api`的行为，请和`Onebot`的连接方式进行匹配)
  - `ws_server`: `im_api`启动ws_server，适用于Onebot的`反向ws`或者`Websocket客户端`模式
  - `ws_client`: `im_api`启动ws_client，适用于Onebot的`正向ws`或者`Websocket服务器`模式
- `ws_server`: （当 connection_type 为 ws_server 时使用）
  - `host`: 监听地址
  - `port`: 监听端口
  - `access_token`: 访问令牌，留空则不验证
  - `url_prefix`: WebSocket URL前缀
- `ws_client`:（当 connection_type 为 ws_client 时使用）
  - `ws_url`: WebSocket 服务器地址
  - `access_token`: 访问令牌，留空则不验证
  - `heartbeat`: 心跳间隔，单位为秒

### Telegram 平台配置

- `enabled`: 是否启用 Telegram 平台
- `platform`: 平台标识符，固定为 "telegram"
- `token`: Telegram Bot Token
- `http_proxy`: HTTP 代理地址（可选）

### Matrix 平台配置

- `enabled`: 是否启用 Matrix 平台
- `platform`: 平台标识符，固定为 "matrix"
- `account`: 账号配置
  - `user_id`: Matrix 用户 ID
  - `token`: 访问令牌
- `homeserver`: Matrix 服务器地址

## 配置示例

### 最小化配置（仅启用 QQ）

```yaml
drivers:
  # QQ 驱动配置，Onebot的连接方式为反向ws或者Websocket客户端模式
  - enabled: true
    platform: qq
    connection_type: ws_server
    ws_server:
      host: 0.0.0.0
      port: 8080
      access_token: ""
      url_prefix: /ws/
```

### 完整配置（启用所有平台）

```yaml
drivers:
  # QQ 驱动配置
  - enabled: true
    platform: qq
    connection_type: ws_server
    ws_server:
      host: 0.0.0.0
      port: 8080
      access_token: "your_access_token"
      url_prefix: /ws/
    ws_client:
      ws_url: ws://127.0.0.1:6700
      access_token: "your_access_token"
      heartbeat: 30

  # Telegram 驱动配置
  - enabled: true
    platform: telegram
    token: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    http_proxy: "http://127.0.0.1:1080"

  # Matrix 驱动配置
  - enabled: true
    platform: matrix
    account:
      user_id: "@mcdr_bot:matrix.org"
      token: "your_matrix_access_token"
    homeserver: "matrix.org"
```

## 配置最佳实践

1. **安全性考虑**
   - 确保配置文件权限设置正确，防止未授权访问
   - 不要在公共环境中暴露敏感信息
   - 建议使用环境变量或配置文件加密存储敏感信息

2. **性能优化**
   - 只启用需要的平台
   - 合理设置重连间隔，避免频繁重连

3. **稳定性保证**
   - 使用可靠的代理服务器
   - 定期检查并更新配置
   - 保持日志监控，及时发现问题

## 常见问题

1. **配置文件不生效**
   - 检查配置文件路径是否正确
   - 确认 YAML 格式是否正确
   - 重启 MCDR 服务器

2. **平台连接失败**
   - 验证账号信息是否正确
   - 检查网络连接是否正常
   - 确认代理配置是否正确

3. **消息发送失败**
   - 检查平台权限设置
   - 确认目标频道/群组是否可访问
   - 查看错误日志获取详细信息