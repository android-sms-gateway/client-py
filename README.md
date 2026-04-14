# 📱 SMSGate Python API Client

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/blob/master/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![Python Version](https://img.shields.io/pypi/pyversions/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![Downloads](https://img.shields.io/pypi/dm/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![GitHub Issues](https://img.shields.io/github/issues/android-sms-gateway/client-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/issues)
[![GitHub Stars](https://img.shields.io/github/stars/android-sms-gateway/client-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/android-sms-gateway/client-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/network)
[![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/android-sms-gateway/client-py?style=for-the-badge)](https://www.coderabbit.ai)

A modern Python client for seamless integration with the [SMSGate](https://sms-gate.app) API. Send SMS messages programmatically through your Android devices with this powerful yet simple-to-use library.

## 📖 About The Project

The Python client for SMSGate provides a clean, type-safe interface to interact with the SMSGate API. It's designed specifically for Python developers who need to integrate SMS functionality into their applications with minimal setup and maximum reliability.

Key value propositions:

- 🐍 **Pythonic API** - Designed with Python conventions and best practices in mind
- 🛡️ **Robust Security** - Guidance for secure credential handling and optional end‑to‑end encryption
- 🔄 **Flexible Architecture** - Supports both synchronous and asynchronous programming patterns
- 💻 **Type Safety** - Full type hinting for better developer experience and fewer runtime errors
- 🔗 **Webhook Integration** - Simplified webhook management for event-driven architectures

This client abstracts away the complexities of the underlying HTTP API while providing all the necessary functionality to send and track SMS messages through Android devices.

## 📚 Table of Contents
- [📱 SMSGate Python API Client](#-smsgate-python-api-client)
  - [📖 About The Project](#-about-the-project)
  - [📚 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [⚙️ Requirements](#️-requirements)
  - [📦 Installation](#-installation)
    - [Basic Installation](#basic-installation)
    - [Installation with Specific HTTP Client](#installation-with-specific-http-client)
    - [Installation with Encryption](#installation-with-encryption)
  - [🚀 Quickstart](#-quickstart)
    - [Initial Setup](#initial-setup)
    - [Encryption Example](#encryption-example)
    - [JWT Authentication Example](#jwt-authentication-example)
  - [🤖 Client Guide](#-client-guide)
    - [Client Configuration](#client-configuration)
    - [Available Methods](#available-methods)
      - [Message Methods](#message-methods)
      - [Webhook Methods](#webhook-methods)
      - [Device Methods](#device-methods)
      - [Settings Methods](#settings-methods)
      - [Log Methods](#log-methods)
      - [Health Check Methods](#health-check-methods)
      - [Token Methods](#token-methods)
    - [Data Structures](#data-structures)
      - [Message](#message)
      - [MessageState](#messagestate)
      - [Webhook](#webhook)
      - [Device](#device)
      - [DeviceSettings](#devicesettings)
      - [TokenRequest](#tokenrequest)
      - [TokenResponse](#tokenresponse)
      - [HealthResponse](#healthresponse)
      - [LogEntry](#logentry)
      - [Enums](#enums)
  - [🌐 HTTP Clients](#-http-clients)
    - [Using Specific Clients](#using-specific-clients)
    - [Custom HTTP Client](#custom-http-client)
  - [🔒 Security](#-security)
    - [Best Practices](#best-practices)
    - [JWT Security Best Practices](#jwt-security-best-practices)
    - [Secure Configuration Example](#secure-configuration-example)
  - [📚 API Reference](#-api-reference)
  - [👥 Contributing](#-contributing)
    - [How to Contribute](#how-to-contribute)
    - [Development Environment](#development-environment)
    - [Pull Request Checklist](#pull-request-checklist)
  - [📄 License](#-license)
  - [🤝 Support](#-support)


## ✨ Features

- 🔄 **Dual Client**: Supports both synchronous (`APIClient`) and asynchronous (`AsyncAPIClient`) interfaces
- 🔐 **Flexible Authentication**: Supports both Basic Auth and JWT token authentication
- 🔒 **End-to-End Encryption**: Optional message encryption using AES-256-CBC
- 🌐 **Multiple HTTP Backends**: Native support for `requests`, `aiohttp`, and `httpx`
- 🔗 **Webhook Management**: Programmatically create, query, and delete webhooks
- ⚙️ **Customizable Base URL**: Point to different API endpoints
- 💻 **Full Type Hinting**: Fully typed for better development experience
- ⚠️ **Robust Error Handling**: Specific exceptions and clear error messages
- 📈 **Delivery Reports**: Track your message delivery status
- 🔑 **Token Management**: Generate, refresh, and revoke JWT tokens with custom scopes and TTL
- 📊 **Message Filtering**: List messages with date range, state, and device filtering
- ⚙️ **Settings Management**: Get, update, and patch device settings
- 📝 **Logging**: Retrieve system logs with time range filtering
- 🏥 **Health Checks**: Liveness, readiness, and startup probes
- 📱 **Device Management**: List and remove registered devices
- 📥 **Inbox Export**: Export received messages via webhooks

## ⚙️ Requirements

- **Python**: 3.9 or higher
- **HTTP Client** (choose one):
  - 🚀 [requests](https://pypi.org/project/requests/) (synchronous)
  - ⚡ [aiohttp](https://pypi.org/project/aiohttp/) (asynchronous)
  - 🌈 [httpx](https://pypi.org/project/httpx/) (synchronous + asynchronous)

**Optional Dependencies**:
- 🔒 [pycryptodome](https://pypi.org/project/pycryptodome/) - For end-to-end encryption support

## 📦 Installation

### Basic Installation

```bash
pip install android-sms-gateway
```

### Installation with Specific HTTP Client

```bash
# Choose an HTTP client:
pip install android-sms-gateway[requests]    # For synchronous use
pip install android-sms-gateway[aiohttp]     # For asynchronous use
pip install android-sms-gateway[httpx]       # For both synchronous and asynchronous use
```

### Installation with Encryption

```bash
# For encrypted messages:
pip install android-sms-gateway[encryption]

# Or install everything:
pip install android-sms-gateway[requests,encryption]
```

## 🚀 Quickstart

### Initial Setup

1. **Configure your credentials**:
   ```bash
   export SMSGATE_USERNAME="your_username"
   export SMSGATE_PASSWORD="your_password"
   ```

2. **Basic usage example**:

```python
import asyncio
import os

from android_sms_gateway import client, domain

# Configuration
login = os.getenv("SMSGATE_USERNAME")
password = os.getenv("SMSGATE_PASSWORD")

# Create message
message = domain.Message(
    phone_numbers=["+1234567890"],
    text_message=domain.TextMessage(
        text="Hello! This is a test message.",
    ),
    with_delivery_report=True,
)

# Synchronous Client
def sync_example():
    with client.APIClient(login, password) as c:
        # Send message
        response = c.send(message)
        print(f"Message sent with ID: {response.id}")
        
        # Check status
        status = c.get_state(response.id)
        print(f"Status: {status.state}")

# Asynchronous Client
async def async_example():
    async with client.AsyncAPIClient(login, password) as c:
        # Send message
        response = await c.send(message)
        print(f"Message sent with ID: {response.id}")
        
        # Check status
        status = await c.get_state(response.id)
        print(f"Status: {status.state}")

if __name__ == "__main__":
    print("=== Synchronous Example ===")
    sync_example()
    
    print("\n=== Asynchronous Example ===")
    asyncio.run(async_example())
```

### Encryption Example

```python
from android_sms_gateway import client, domain, Encryptor

# Encryption setup
encryptor = Encryptor("my-super-secure-secret-passphrase")

# Encrypted message
message = domain.Message(
    phone_numbers=["+1234567890"],
    text_message=domain.TextMessage(
        text="This message will be encrypted!"
    ),
)

# Client with encryption
with client.APIClient(login, password, encryptor=encryptor) as c:
    response = c.send(message)
    print(f"Encrypted message sent: {response.id}")
```

### JWT Authentication Example

```python
import os
from android_sms_gateway import client, domain

# Option 1: Using an existing JWT token
jwt_token = os.getenv("ANDROID_SMS_GATEWAY_JWT_TOKEN")

# Create client with JWT token
with client.APIClient(login=None, password=jwt_token) as c:
    message = domain.Message(
        phone_numbers=["+1234567890"],
        text_message=domain.TextMessage(
            text="Hello from JWT authenticated client!",
        ),
    )

# Option 2: Generate a new JWT token with Basic Auth
login = os.getenv("SMSGATE_USERNAME")
password = os.getenv("SMSGATE_PASSWORD")

with client.APIClient(login, password) as c:
    # Generate a new JWT token with specific scopes and TTL
    token_request = domain.TokenRequest(
        scopes=["sms:send", "sms:read"],
        ttl=3600  # Token expires in 1 hour
    )
    token_response = c.generate_token(token_request)
    print(f"New JWT token: {token_response.access_token}")
    print(f"Token expires at: {token_response.expires_at}")
    
    # Use the new token for subsequent requests
    with client.APIClient(login=None, password=token_response.access_token) as jwt_client:
        message = domain.Message(
            phone_numbers=["+1234567890"],
            text_message=domain.TextMessage(
                text="Hello from newly generated JWT token!",
            ),
        )
        response = jwt_client.send(message)
        print(f"Message sent with new JWT token: {response.id}")
        
        # Revoke the token when no longer needed
        jwt_client.revoke_token(token_response.id)
        print(f"Token {token_response.id} has been revoked")
```

## 🤖 Client Guide

### Client Configuration

Both clients (`APIClient` and `AsyncAPIClient`) support these parameters:

| Parameter   | Type                           | Description               | Default                                  |
| ----------- | ------------------------------ | ------------------------- | ---------------------------------------- |
| `login`     | `str`                          | API username              | **Required** (for Basic Auth)            |
| `password`  | `str`                          | API password or JWT token | **Required**                             |
| `base_url`  | `str`                          | API base URL              | `"https://api.sms-gate.app/3rdparty/v1"` |
| `encryptor` | `Encryptor`                    | Encryption instance       | `None`                                   |
| `http`      | `HttpClient`/`AsyncHttpClient` | Custom HTTP client        | Auto-detected                            |

**Authentication Options:**

1. **Basic Authentication** (traditional):
   ```python
   client.APIClient(login="username", password="password")
   ```

2. **JWT Token Authentication**:
   ```python
   # Using an existing JWT token
   client.APIClient(login=None, password="your_jwt_token")
   
   # Or generate a token using Basic Auth first
   with client.APIClient(login="username", password="password") as c:
       token_request = domain.TokenRequest(scopes=["sms:send"], ttl=3600)
       token_response = c.generate_token(token_request)
       
       # Use the new token
       with client.APIClient(login=None, password=token_response.access_token) as jwt_client:
           # Make API calls with JWT authentication
           pass
   ```

### Available Methods

#### Message Methods

| Method                                                                  | Description                        | Return Type                 |
| ----------------------------------------------------------------------- | ---------------------------------- | --------------------------- |
| `send(message, *, skip_phone_validation=False, device_active_within=0)` | Send SMS message                   | `domain.MessageState`       |
| `get_state(id)`                                                         | Get message state by ID            | `domain.MessageState`       |
| `get_messages(*, filter=None, pagination=None)`                         | List messages with filtering       | `List[domain.MessageState]` |
| `export_inbox(request)`                                                 | Export inbox messages via webhooks | `dict`                      |

#### Webhook Methods

| Method                    | Description        | Return Type            |
| ------------------------- | ------------------ | ---------------------- |
| `create_webhook(webhook)` | Create new webhook | `domain.Webhook`       |
| `get_webhooks()`          | List all webhooks  | `List[domain.Webhook]` |
| `delete_webhook(id)`      | Delete webhook     | `None`                 |

#### Device Methods

| Method              | Description                 | Return Type           |
| ------------------- | --------------------------- | --------------------- |
| `list_devices()`    | List all registered devices | `List[domain.Device]` |
| `remove_device(id)` | Remove a device             | `None`                |

#### Settings Methods

| Method                      | Description               | Return Type             |
| --------------------------- | ------------------------- | ----------------------- |
| `get_settings()`            | Get device settings       | `domain.DeviceSettings` |
| `update_settings(settings)` | Replace settings          | `dict`                  |
| `patch_settings(settings)`  | Partially update settings | `dict`                  |

#### Log Methods

| Method                          | Description     | Return Type             |
| ------------------------------- | --------------- | ----------------------- |
| `get_logs(from_=None, to=None)` | Get log entries | `List[domain.LogEntry]` |

#### Health Check Methods

| Method              | Description     | Return Type             |
| ------------------- | --------------- | ----------------------- |
| `health_check()`    | Readiness probe | `domain.HealthResponse` |
| `liveness_check()`  | Liveness probe  | `domain.HealthResponse` |
| `readiness_check()` | Readiness probe | `domain.HealthResponse` |
| `startup_check()`   | Startup probe   | `domain.HealthResponse` |

#### Token Methods

| Method                          | Description          | Return Type            |
| ------------------------------- | -------------------- | ---------------------- |
| `generate_token(token_request)` | Generate JWT token   | `domain.TokenResponse` |
| `refresh_token(refresh_token)`  | Refresh access token | `domain.TokenResponse` |
| `revoke_token(jti)`             | Revoke JWT token     | `None`                 |

### Data Structures

#### Message

```python
class Message:
    phone_numbers: List[str]           # List of phone numbers (required)
    text_message: Optional[TextMessage] = None  # Text message
    data_message: Optional[DataMessage] = None  # Data message
    priority: Optional[MessagePriority] = None  # Message priority
    sim_number: Optional[int] = None   # SIM card number (1-3)
    with_delivery_report: bool = True  # Delivery report
    is_encrypted: bool = False         # Whether message is encrypted
    ttl: Optional[int] = None          # Time-to-live in seconds
    valid_until: Optional[datetime] = None  # Valid until timestamp
    id: Optional[str] = None           # Message ID
    device_id: Optional[str] = None    # Device ID for explicit selection
```

#### MessageState

```python
class MessageState:
    id: str                            # Unique message ID
    state: ProcessState                # Current processing state
    recipients: List[RecipientState]   # Per-recipient status
    is_hashed: bool = False            # Whether phone numbers are hashed
    is_encrypted: bool = False         # Whether message was encrypted
    device_id: Optional[str] = None    # Device ID (optional for backward compatibility)
    states: Optional[Dict[str, str]] = None  # History of state changes
```

#### Webhook

```python
class Webhook:
    id: Optional[str]               # Webhook ID
    url: str                        # Callback URL
    event: WebhookEvent             # Event type
    device_id: Optional[str] = None # Associated device ID
```

#### Device

```python
class Device:
    id: str                         # Unique device identifier
    name: str                       # Device name
    created_at: Optional[datetime] = None  # Creation timestamp
    updated_at: Optional[datetime] = None  # Last update timestamp
    deleted_at: Optional[datetime] = None  # Deletion timestamp
    last_seen: Optional[datetime] = None   # Last seen timestamp
```

#### DeviceSettings

```python
class DeviceSettings:
    gateway: Optional[SettingsGateway] = None      # Gateway settings
    encryption: Optional[SettingsEncryption] = None # Encryption settings
    messages: Optional[SettingsMessages] = None     # Message handling settings
    logs: Optional[SettingsLogs] = None            # Logging settings
    ping: Optional[SettingsPing] = None            # Ping settings
    webhooks: Optional[SettingsWebhooks] = None    # Webhook settings
```

#### TokenRequest

```python
class TokenRequest:
    scopes: List[str]               # List of scopes for the token (required)
    ttl: Optional[int] = None       # Time to live in seconds
```

#### TokenResponse

```python
class TokenResponse:
    access_token: str               # The JWT access token
    token_type: str                 # Token type (e.g., 'Bearer')
    id: str                         # Unique token identifier (jti)
    expires_at: str                 # Expiration time in ISO format
    refresh_token: Optional[str] = None  # Refresh token
```

#### HealthResponse

```python
class HealthResponse:
    status: HealthStatus            # Overall health status
    version: Optional[str] = None   # Application version
    release_id: Optional[int] = None # Release ID
    checks: Optional[Dict[str, HealthCheck]] = None  # Individual health checks
```

#### LogEntry

```python
class LogEntry:
    id: int                         # Unique log entry ID
    created_at: datetime            # Creation timestamp
    message: str                    # Log message
    priority: LogEntryPriority      # Priority level (DEBUG, INFO, WARN, ERROR)
    module: Optional[str] = None    # Source module
    context: Optional[Dict] = None  # Additional context
```

#### Enums

```python
class ProcessState(enum.Enum):
    Pending = "Pending"
    Processed = "Processed"
    Sent = "Sent"
    Delivered = "Delivered"
    Failed = "Failed"

class WebhookEvent(enum.Enum):
    SMS_RECEIVED = "sms:received"
    SMS_DATA_RECEIVED = "sms:data-received"
    SMS_SENT = "sms:sent"
    SMS_DELIVERED = "sms:delivered"
    SMS_FAILED = "sms:failed"
    SYSTEM_PING = "system:ping"
    MMS_RECEIVED = "mms:received"
    MMS_DOWNLOADED = "mms:downloaded"

class MessagePriority(enum.IntEnum):
    MINIMUM = -128
    DEFAULT = 0
    BYPASS_THRESHOLD = 100
    MAXIMUM = 127

class LimitPeriod(enum.Enum):
    DISABLED = "Disabled"
    PER_MINUTE = "PerMinute"
    PER_HOUR = "PerHour"
    PER_DAY = "PerDay"

class SimSelectionMode(enum.Enum):
    OS_DEFAULT = "OSDefault"
    ROUND_ROBIN = "RoundRobin"
    RANDOM = "Random"

class MessagesProcessingOrder(enum.Enum):
    LIFO = "LIFO"
    FIFO = "FIFO"

class HealthStatus(enum.Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"

class LogEntryPriority(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
```

For more details, see [`domain.py`](./android_sms_gateway/domain.py).

## 🌐 HTTP Clients

The library automatically detects installed HTTP clients with this priority:

| Client   | Sync | Async |
| -------- | ---- | ----- |
| aiohttp  | ❌    | 1️⃣     |
| requests | 1️⃣    | ❌     |
| httpx    | 2️⃣    | 2️⃣     |

### Using Specific Clients

```python
from android_sms_gateway import client, http

# Force httpx usage
client.APIClient(..., http=http.HttpxHttpClient())

# Force requests usage
client.APIClient(..., http=http.RequestsHttpClient())

# Force aiohttp (async only)
async with client.AsyncAPIClient(..., http_client=http.AiohttpHttpClient()) as c:
    # ...
```

### Custom HTTP Client

Implement your own HTTP client following the `http.HttpClient` (sync) or `ahttp.AsyncHttpClient` (async) protocols.

## 🔒 Security

### Best Practices

⚠️ **IMPORTANT**: Always follow these security practices:

- 🔐 **Credentials**: Store credentials in environment variables
- 🚫 **Code**: Never expose credentials in client-side code
- 🔒 **HTTPS**: Use HTTPS for all production communications
- 🔑 **Encryption**: Use end-to-end encryption for sensitive messages
- 🔄 **Rotation**: Regularly rotate your credentials

### JWT Security Best Practices

When using JWT authentication, follow these additional security practices:

- ⏱️ **Short TTL**: Use short time-to-live (TTL) for tokens (recommended: 1 hour or less)
- 🔒 **Secure Storage**: Store JWT tokens securely, preferably in memory or secure storage
- 🎯 **Minimal Scopes**: Request only the minimum necessary scopes for each token
- 🔄 **Token Rotation**: Implement token refresh mechanisms before expiration
- 🛑 **Revocation**: Immediately revoke compromised tokens using `revoke_token()`

### Secure Configuration Example

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Secure configuration
login = os.getenv("SMSGATE_USERNAME")
password = os.getenv("SMSGATE_PASSWORD")

if not login or not password:
    raise ValueError("Credentials not configured!")
```

## 📚 API Reference

For complete API documentation including all available methods, request/response schemas, and error codes, visit:
[📘 Official API Documentation](https://docs.sms-gate.app/integration/api/)

## 👥 Contributing

Contributions are very welcome! 🎉

### How to Contribute

1. 🍴 Fork the repository
2. 🌿 Create your feature branch (`git checkout -b feature/NewFeature`)
3. 💾 Commit your changes (`git commit -m 'feat: add new feature'`)
4. 📤 Push to branch (`git push origin feature/NewFeature`)
5. 🔄 Open a Pull Request

### Development Environment

```bash
# Clone repository
git clone https://github.com/android-sms-gateway/client-py.git
cd client-py

# Create virtual environment
pipenv install --dev --categories encryption,requests
pipenv shell
```

### Pull Request Checklist

- [ ] Code follows style standards (black, isort, flake8)
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Test coverage maintained or improved

## 📄 License

This project is licensed under the **Apache License 2.0** - see [LICENSE](LICENSE) for details.

## 🤝 Support

- 📧 **Email**: [support@sms-gate.app](mailto:support@sms-gate.app)
- 💬 **Discord**: [SMS Gateway Community](https://discord.gg/vv9raFK4gX)
- 📖 **Documentation**: [docs.sms-gate.app](https://docs.sms-gate.app)
- 🐛 **Issues**: [GitHub Issues](https://github.com/android-sms-gateway/client-py/issues)

---

**Note**: Android is a trademark of Google LLC. This project is not affiliated with or endorsed by Google.
