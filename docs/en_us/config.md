# Configuration Guide

This document will guide you on how to configure ImAPI, including the structure of the default configuration file, detailed explanation of each configuration item, and specific configuration methods for different platforms.

## Configuration File Structure

ImAPI uses YAML format configuration files. The default configuration file is located at `im_api/config.default.yml`, and you need to copy it to the MCDR configuration directory and rename it to `config/im_api/config.yml`.

Here's the basic structure of the configuration file:

```yaml
drivers:
  qq:  # QQ platform configuration
    enabled: true  # Whether to enable
    account:  # Account configuration
      uin: 123456789  # QQ number
      password: "your_password"  # Password, recommended to wrap with quotes
    protocol: 2  # Login protocol, 1: Android Phone, 2: Android Watch, 3: Android Pad
    reconnect_interval: 10  # Reconnection interval (seconds)

  telegram:  # Telegram platform configuration
    enabled: true  # Whether to enable
    token: "your_bot_token"  # Bot Token
    proxy:  # Proxy configuration (optional)
      enabled: false
      type: socks5  # Supports socks5/http
      host: 127.0.0.1
      port: 1080
      username: ""  # Optional
      password: ""  # Optional

  matrix:  # Matrix platform configuration
    enabled: false  # Whether to enable
    homeserver: "https://matrix.org"  # Matrix server address
    user_id: "@your_user:matrix.org"  # User ID
    access_token: "your_access_token"  # Access token
```

## Configuration Items

### QQ Platform Configuration

- `enabled`: Whether to enable QQ platform
- `account`:
  - `uin`: QQ account number
  - `password`: QQ password
- `protocol`: Login protocol type
  - `1`: Android Phone
  - `2`: Android Watch
  - `3`: Android Pad
- `reconnect_interval`: Disconnection reconnection interval in seconds

### Telegram Platform Configuration

- `enabled`: Whether to enable Telegram platform
- `token`: Telegram Bot Token, obtained from @BotFather
- `proxy`: Proxy configuration (optional)
  - `enabled`: Whether to enable proxy
  - `type`: Proxy type, supports socks5 and http
  - `host`: Proxy server address
  - `port`: Proxy server port
  - `username`: Proxy authentication username (optional)
  - `password`: Proxy authentication password (optional)

### Matrix Platform Configuration

- `enabled`: Whether to enable Matrix platform
- `homeserver`: Matrix server address
- `user_id`: Matrix user ID
- `access_token`: Matrix access token

## Configuration Examples

### Minimal Configuration (QQ Only)

```yaml
drivers:
  qq:
    enabled: true
    account:
      uin: 123456789
      password: "your_password"
    protocol: 1
    reconnect_interval: 10
  telegram:
    enabled: false
  matrix:
    enabled: false
```

### Complete Configuration (All Platforms Enabled)

```yaml
drivers:
  qq:
    enabled: true
    account:
      uin: 123456789
      password: "your_secure_password"
    protocol: 2
    reconnect_interval: 10

  telegram:
    enabled: true
    token: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    proxy:
      enabled: true
      type: socks5
      host: 127.0.0.1
      port: 1080

  matrix:
    enabled: true
    homeserver: "https://matrix.org"
    user_id: "@mcdr_bot:matrix.org"
    access_token: "your_matrix_access_token"
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