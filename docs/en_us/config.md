# Configuration Guide

This document will guide you on how to configure ImAPI, including the structure of the default configuration file, detailed explanation of each configuration item, and specific configuration methods for different platforms.

## Configuration File Structure

ImAPI uses YAML format configuration files. MCDR will initialize this configuration file to `config/im_api/config.yml` when loading im_api for the first time. You need to modify the configuration file after the first load for it to work properly.

Here's the basic structure of the configuration file:

```yaml
drivers:
  # QQ driver configuration
  - enabled: true
    platform: qq
    # Connection type: ws_server(Onebot Reverse WS) or ws_client(Onebot Forward WS)
    connection_type: ws_server
    # Reverse WebSocket configuration (used when connection_type is ws_server)
    ws_server:
      host: 0.0.0.0
      port: 8080
      access_token: ""   # Access token, leave empty for no validation
      url_prefix: /ws/   # WebSocket URL prefix
    
    # Forward WebSocket configuration (used when connection_type is ws_client)
    ws_client:
      ws_url: ws://127.0.0.1:6700
      access_token: ""   # Access token, leave empty for no validation
      heartbeat: 30  # Heartbeat interval (seconds)
  
  # Telegram driver configuration
  - enabled: false
    platform: telegram
    token: ""
    http_proxy: ""

  # Matrix driver configuration
  - enabled: false
    platform: matrix
    account:
      user_id: ""
      token: ""
    homeserver: "example.com"
```

## Configuration Items

### QQ Platform Configuration

- `enabled`: Whether to enable QQ platform
- `platform`: Platform identifier, fixed as "qq"
- `connection_type`: Connection type (Note: This is the behavior of `im_api`, please match with Onebot's connection method)
  - `ws_server`: `im_api` starts ws_server, suitable for Onebot's `Reverse WS` or `WebSocket Client` mode
  - `ws_client`: `im_api` starts ws_client, suitable for Onebot's `Forward WS` or `WebSocket Server` mode
- `ws_server`: (Used when connection_type is ws_server)
  - `host`: Listening address
  - `port`: Listening port
  - `access_token`: Access token, leave empty for no validation
  - `url_prefix`: WebSocket URL prefix
- `ws_client`: (Used when connection_type is ws_client)
  - `ws_url`: WebSocket server address
  - `access_token`: Access token, leave empty for no validation
  - `heartbeat`: Heartbeat interval in seconds

### Telegram Platform Configuration

- `enabled`: Whether to enable Telegram platform
- `platform`: Platform identifier, fixed as "telegram"
- `token`: Telegram Bot Token
- `http_proxy`: HTTP proxy address (optional)

### Matrix Platform Configuration

- `enabled`: Whether to enable Matrix platform
- `platform`: Platform identifier, fixed as "matrix"
- `account`: Account configuration
  - `user_id`: Matrix user ID
  - `token`: Access token
- `homeserver`: Matrix server address

## Configuration Examples

### Minimal Configuration (QQ Only)

```yaml
drivers:
  # QQ driver configuration, Onebot connection method is Reverse WS or WebSocket Client mode
  - enabled: true
    platform: qq
    connection_type: ws_server
    ws_server:
      host: 0.0.0.0
      port: 8080
      access_token: ""
      url_prefix: /ws/
```

### Complete Configuration (All Platforms Enabled)

```yaml
drivers:
  # QQ driver configuration
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

  # Telegram driver configuration
  - enabled: true
    platform: telegram
    token: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    http_proxy: "http://127.0.0.1:1080"

  # Matrix driver configuration
  - enabled: true
    platform: matrix
    account:
      user_id: "@mcdr_bot:matrix.org"
      token: "your_matrix_access_token"
    homeserver: "matrix.org"
```

## Best Practices

1. **Security Considerations**
   - Ensure correct configuration file permissions to prevent unauthorized access
   - Don't expose sensitive information in public environments
   - Recommend using environment variables or encrypted configuration files to store sensitive information

2. **Performance Optimization**
   - Only enable needed platforms
   - Set reasonable reconnection intervals to avoid frequent reconnections

3. **Stability Assurance**
   - Use reliable proxy servers
   - Regularly check and update configurations
   - Maintain log monitoring to detect issues promptly

## Common Issues

1. **Configuration File Not Taking Effect**
   - Check if the configuration file path is correct
   - Verify if the YAML format is correct
   - Restart the MCDR server

2. **Platform Connection Failure**
   - Verify if account information is correct
   - Check if network connection is normal
   - Confirm if proxy configuration is correct

3. **Message Sending Failure**
   - Check platform permission settings
   - Confirm if target channel/group is accessible
   - View error logs for detailed information