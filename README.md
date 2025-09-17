# 📱 SMS Gateway for Android™ Python API Client

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/blob/master/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![Python Version](https://img.shields.io/pypi/pyversions/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![Downloads](https://img.shields.io/pypi/dm/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![GitHub Issues](https://img.shields.io/github/issues/android-sms-gateway/client-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/issues)
[![GitHub Stars](https://img.shields.io/github/stars/android-sms-gateway/client-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/android-sms-gateway/client-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/network)
[![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/android-sms-gateway/client-py?style=for-the-badge)](https://www.coderabbit.ai)

A modern Python client for seamless integration with the [SMS Gateway for Android](https://sms-gate.app) API. Send SMS messages programmatically through your Android devices with this powerful yet simple-to-use library.

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
- [📱 SMS Gateway for Android™ Python API Client](#-sms-gateway-for-android-python-api-client)
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
  - [🤖 Client Guide](#-client-guide)
    - [Client Configuration](#client-configuration)
    - [Available Methods](#available-methods)
    - [Data Structures](#data-structures)
      - [Message](#message)
      - [MessageState](#messagestate)
      - [Webhook](#webhook)
  - [🌐 HTTP Clients](#-http-clients)
    - [Using Specific Clients](#using-specific-clients)
    - [Custom HTTP Client](#custom-http-client)
  - [🔒 Security](#-security)
    - [Best Practices](#best-practices)
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
- 🔒 **End-to-End Encryption**: Optional message encryption using AES-256-CBC
- 🌐 **Multiple HTTP Backends**: Native support for `requests`, `aiohttp`, and `httpx`
- 🔗 **Webhook Management**: Programmatically create, query, and delete webhooks
- ⚙️ **Customizable Base URL**: Point to different API endpoints
- 💻 **Full Type Hinting**: Fully typed for better development experience
- ⚠️ **Robust Error Handling**: Specific exceptions and clear error messages
- 📈 **Delivery Reports**: Track your message delivery status

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
   export ANDROID_SMS_GATEWAY_LOGIN="your_username"
   export ANDROID_SMS_GATEWAY_PASSWORD="your_password"
   ```

2. **Basic usage example**:

```python
import asyncio
import os

from android_sms_gateway import client, domain

# Configuration
login = os.getenv("ANDROID_SMS_GATEWAY_LOGIN")
password = os.getenv("ANDROID_SMS_GATEWAY_PASSWORD")

# Create message
message = domain.Message(
    "Hello! This is a test message.",
    ["+1234567890"],
    with_delivery_report=True
)

# Synchronous Client
def sync_example():
    with client.APIClient(login, password) as c:
        # Send message
        state = c.send(message)
        print(f"Message sent with ID: {state.id}")
        
        # Check status
        status = c.get_state(state.id)
        print(f"Status: {status.state}")

# Asynchronous Client
async def async_example():
    async with client.AsyncAPIClient(login, password) as c:
        # Send message
        state = await c.send(message)
        print(f"Message sent with ID: {state.id}")
        
        # Check status
        status = await c.get_state(state.id)
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
    "This message will be encrypted!",
    ["+1234567890"],
    is_encrypted=True
)

# Client with encryption
with client.APIClient(login, password, encryptor=encryptor) as c:
    state = c.send(message)
    print(f"Encrypted message sent: {state.id}")
```

## 🤖 Client Guide

### Client Configuration

Both clients (`APIClient` and `AsyncAPIClient`) support these parameters:

| Parameter   | Type                           | Description         | Default                                  |
| ----------- | ------------------------------ | ------------------- | ---------------------------------------- |
| `login`     | `str`                          | API username        | **Required**                             |
| `password`  | `str`                          | API password        | **Required**                             |
| `base_url`  | `str`                          | API base URL        | `"https://api.sms-gate.app/3rdparty/v1"` |
| `encryptor` | `Encryptor`                    | Encryption instance | `None`                                   |
| `http`      | `HttpClient`/`AsyncHttpClient` | Custom HTTP client  | Auto-detected                            |

### Available Methods

| Method                                    | Description          | Return Type            |
| ----------------------------------------- | -------------------- | ---------------------- |
| `send(message: domain.Message)`           | Send SMS message     | `domain.MessageState`  |
| `get_state(id: str)`                      | Check message status | `domain.MessageState`  |
| `create_webhook(webhook: domain.Webhook)` | Create new webhook   | `domain.Webhook`       |
| `get_webhooks()`                          | List all webhooks    | `List[domain.Webhook]` |
| `delete_webhook(id: str)`                 | Delete webhook       | `None`                 |

### Data Structures

#### Message

```python
class Message:
    message: str                       # Message text
    phone_numbers: List[str]           # List of phone numbers
    with_delivery_report: bool = True  # Delivery report
    is_encrypted: bool = False         # Whether message is encrypted
    
    # Optional fields
    id: Optional[str] = None         # Message ID
    ttl: Optional[int] = None        # Time-to-live in seconds
    sim_number: Optional[int] = None # SIM number
```

#### MessageState

```python
class MessageState:
    id: str                          # Unique message ID
    state: ProcessState              # Current state (SENT, DELIVERED, etc.)
    recipients: List[RecipientState] # Per-recipient status
    is_hashed: bool                  # Whether message was hashed
    is_encrypted: bool               # Whether message was encrypted
```

#### Webhook

```python
class Webhook:
    id: Optional[str]               # Webhook ID
    url: str                        # Callback URL
    event: WebhookEvent             # Event type
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
async with client.AsyncAPIClient(..., http=http.AiohttpHttpClient()) as c:
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

### Secure Configuration Example

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Secure configuration
login = os.getenv("ANDROID_SMS_GATEWAY_LOGIN")
password = os.getenv("ANDROID_SMS_GATEWAY_PASSWORD")

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
