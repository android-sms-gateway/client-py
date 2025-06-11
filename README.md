# 📱 SMS Gateway for Android™ Python API Client

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/blob/master/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![Python Version](https://img.shields.io/pypi/pyversions/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![Downloads](https://img.shields.io/pypi/dm/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![GitHub Issues](https://img.shields.io/github/issues/capcom6/android-sms-gateway-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/issues)
[![GitHub Stars](https://img.shields.io/github/stars/capcom6/android-sms-gateway-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/capcom6/android-sms-gateway-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/network)

A modern Python client for seamless integration with the [SMS Gateway for Android](https://sms-gate.app) API. Send SMS messages programmatically through your Android devices with this powerful yet simple-to-use library.

## 📖 Table of Contents
- [📱 SMS Gateway for Android™ Python API Client](#-sms-gateway-for-android-python-api-client)
  - [📖 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [⚙️ Requirements](#️-requirements)
  - [📦 Installation](#-installation)
  - [🚀 Quickstart](#-quickstart)
    - [Basic Usage](#basic-usage)
  - [🤖 Client Guide](#-client-guide)
    - [Client Configuration](#client-configuration)
    - [Core Methods](#core-methods)
    - [Type Definitions](#type-definitions)
    - [Encryption Setup](#encryption-setup)
  - [🌐 HTTP Clients](#-http-clients)
  - [🔒 Security Notes](#-security-notes)
  - [📚 API Reference](#-api-reference)
  - [👥 Contributing](#-contributing)
    - [Development Setup](#development-setup)
  - [📄 License](#-license)

## ✨ Features
- **Dual Client Support**: Choose between synchronous (`APIClient`) and asynchronous (`AsyncAPIClient`) interfaces
- **End-to-End Encryption**: Optional message encryption using AES-CBC-256
- **Multiple HTTP Backends**: Supports `requests`, `aiohttp`, and `httpx`
- **Webhook Management**: Create, read, and delete webhooks
- **Customizable Base URL**: Point to different API endpoints
- **Type Hinting**: Fully typed for better development experience

## ⚙️ Requirements
- Python 3.9+
- Choose one HTTP client:
  - 🚀 [requests](https://pypi.org/project/requests/) (sync)
  - ⚡ [aiohttp](https://pypi.org/project/aiohttp/) (async)
  - 🌈 [httpx](https://pypi.org/project/httpx/) (sync+async)

**Optional**:
- 🔒 [pycryptodome](https://pypi.org/project/pycryptodome/) - For end-to-end encryption support

## 📦 Installation

Install the base package:
```bash
pip install android_sms_gateway
```

Install with your preferred HTTP client:
```bash
# Choose one:
pip install android_sms_gateway[requests]
pip install android_sms_gateway[aiohttp]
pip install android_sms_gateway[httpx]
```

For encrypted messaging:
```bash
pip install android_sms_gateway[encryption]
```

## 🚀 Quickstart

### Basic Usage
```python
import asyncio
import os

from android_sms_gateway import client, domain, Encryptor

login = os.getenv("ANDROID_SMS_GATEWAY_LOGIN")
password = os.getenv("ANDROID_SMS_GATEWAY_PASSWORD")
# for end-to-end encryption, see https://docs.sms-gate.app/privacy/encryption/
# encryptor = Encryptor('passphrase')

message = domain.Message(
    "Your message text here.",
    ["+1234567890"],
)

def sync_client():
    with client.APIClient(
        login, 
        password,
        # encryptor=encryptor,
    ) as c:
        state = c.send(message)
        print(state)

        state = c.get_state(state.id)
        print(state)


async def async_client():
    async with client.AsyncAPIClient(
        login, 
        password,
        # encryptor=encryptor,
    ) as c:
        state = await c.send(message)
        print(state)

        state = await c.get_state(state.id)
        print(state)

print("Sync client")
sync_client()

print("\nAsync client")
asyncio.run(async_client())
```

## 🤖 Client Guide

There are two client classes: `APIClient` and `AsyncAPIClient`. The
`APIClient` is synchronous and the `AsyncAPIClient` is asynchronous. Both
implement the same interface and can be used as context managers.

### Client Configuration

Both clients support the following initialization parameters:

| Argument    | Description        | Default                                  |
| ----------- | ------------------ | ---------------------------------------- |
| `login`     | Username           | **Required**                             |
| `password`  | Password           | **Required**                             |
| `base_url`  | API base URL       | `"https://api.sms-gate.app/3rdparty/v1"` |
| `encryptor` | Encryptor instance | `None`                                   |
| `http`      | Custom HTTP client | Auto-detected                            |

### Core Methods

| Method                                          | Description          | Returns                |
| ----------------------------------------------- | -------------------- | ---------------------- |
| `send(self, message: domain.Message)`           | Send a message       | `domain.MessageState`  |
| `get_state(self, _id: str)`                     | Get message state    | `domain.MessageState`  |
| `create_webhook(self, webhook: domain.Webhook)` | Create a new webhook | `domain.Webhook`       |
| `get_webhooks(self)`                            | Get all webhooks     | `List[domain.Webhook]` |
| `delete_webhook(self, _id: str)`                | Delete a webhook     | `None`                 |


### Type Definitions

```python
class Message:
    message: str
    phone_numbers: t.List[str]
    with_delivery_report: bool = True
    is_encrypted: bool = False

    id: t.Optional[str] = None
    ttl: t.Optional[int] = None
    sim_number: t.Optional[int] = None


class MessageState:
    id: str
    state: ProcessState
    recipients: t.List[RecipientState]
    is_hashed: bool
    is_encrypted: bool


class Webhook:
    id: t.Optional[str]
    url: str
    event: WebhookEvent
```

For more details, see the [`domain.py`](./android_sms_gateway/domain.py).

### Encryption Setup
```python
from android_sms_gateway import client, Encryptor

# Initialize with your secret passphrase
encryptor = Encryptor("my-secret-passphrase")

# Use in client initialization
client.APIClient(login, password, encryptor=encryptor)
```

## 🌐 HTTP Clients
The library automatically detects installed HTTP clients. Here's the priority:

| Client   | Sync | Async |
| -------- | ---- | ----- |
| aiohttp  | ❌    | 1️⃣     |
| requests | 1️⃣    | ❌     |
| httpx    | 2️⃣    | 2️⃣     |

To use a specific client:
```python
# Force httpx sync client
client.APIClient(..., http=http.HttpxHttpClient())
```

You can also implement your own HTTP client that conforms to the `http.HttpClient` or `ahttp.HttpClient` protocol.

## 🔒 Security Notes

⚠️ **Important Security Practices**
- Always store credentials in environment variables
- Never expose credentials in client-side code
- Use HTTPS for all production communications

## 📚 API Reference
For complete API documentation including all available methods, request/response schemas, and error codes, visit:
[📘 Official API Documentation](https://docs.sms-gate.app/integration/api/)

## 👥 Contributing
We welcome contributions! Here's how to help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/android-sms-gateway/client-py.git
cd client-py
pipenv install --dev --categories encryption,requests
pipenv shell
```

## 📄 License
Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for more information.

---

**Note**: Android is a trademark of Google LLC. This project is not affiliated with or endorsed by Google.
