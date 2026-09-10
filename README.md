# 📱 SMSGate Python Client

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stars][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![PyPI Version][version-shield]][version-url]

A modern Python client for the [SMSGate](https://sms-gate.app) API: send SMS messages through your Android devices with synchronous and asynchronous interfaces, Basic or JWT authentication, and optional end-to-end encryption. See the [client libraries overview](https://docs.sms-gate.app/integration/client-libraries/) for the full ecosystem.

## 📖 About

`android-sms-gateway` is a typed Python library for the SMSGate 3rd-party API, with fully type-hinted domain models. It ships a synchronous `APIClient` and an asynchronous `AsyncAPIClient`, auto-detects the installed HTTP backend (`requests`, `aiohttp`, or `httpx`), and supports optional end-to-end message encryption via `Encryptor` (AES-256-CBC). Covers messages, inbox (refresh, attachments), devices, webhooks, settings, logs, health probes, and the JWT token lifecycle.

## 📚 Table of Contents

- [📱 SMSGate Python Client](#-smsgate-python-client)
  - [📖 About](#-about)
  - [📚 Table of Contents](#-table-of-contents)
  - [⭐ Features](#-features)
  - [📦 Installation](#-installation)
  - [🚀 Getting Started](#-getting-started)
    - [Prerequisites](#prerequisites)
    - [Quick Setup](#quick-setup)
  - [🔑 Authentication](#-authentication)
    - [Basic Authentication](#basic-authentication)
    - [JWT Authentication](#jwt-authentication)
  - [🚀 Quickstart](#-quickstart)
  - [💻 Usage](#-usage)
  - [📖 API Reference](#-api-reference)
  - [🗺️ Roadmap](#️-roadmap)
  - [🤝 Contributing](#-contributing)
  - [📞 Contact](#-contact)
  - [📄 License](#-license)
  - [🙏 Acknowledgments](#-acknowledgments)

## ⭐ Features

- Synchronous `APIClient` and asynchronous `AsyncAPIClient` (context managers)
- Basic and JWT authentication; token generate, refresh, and revoke
- HTTP backends: `requests` (sync), `aiohttp` (async), `httpx` (both), auto-detected
- Optional end-to-end encryption via `Encryptor` (AES-256-CBC)
- Webhooks, devices, settings, logs, and health probes (live, ready, startup)
- Inbox refresh with webhook delivery and MMS attachment download
- Full type hints and typed exceptions (`APIError` subclasses)

## 📦 Installation

```bash
pip install android-sms-gateway
```

Requires Python 3.9+. Optional extras:
```bash
pip install android-sms-gateway[requests]    # sync requests backend
pip install android-sms-gateway[aiohttp]     # async aiohttp backend
pip install android-sms-gateway[httpx]       # httpx backend (sync + async)
pip install android-sms-gateway[encryption]  # end-to-end encryption (pycryptodome)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- An [SMSGate](https://sms-gate.app) account with API credentials
- An Android device running the SMSGate app

### Quick Setup

1. Install the library with your preferred HTTP backend:
   ```bash
   pip install android-sms-gateway[requests]
   ```

2. Set environment variables:
   ```bash
   export API_LOGIN="your-login"
   export API_PASSWORD="your-password"
   ```

3. Send your first message:
   ```python
   import os
   from android_sms_gateway import client, domain

   message = domain.Message(
       phone_numbers=["+12025550100"],
       text_message=domain.TextMessage(text="Hello from Python"),
   )

   with client.APIClient(os.getenv("API_LOGIN"), os.getenv("API_PASSWORD")) as c:
       state = c.send(message)
       print(f"Message ID: {state.id}")
   ```

## 🔑 Authentication

Two methods are supported: Basic authentication with account credentials, and JWT bearer tokens with scoped permissions. Pass `login=None` with a token to switch to JWT.

### Basic Authentication

```python
import os

from android_sms_gateway import client, domain

login = os.getenv("API_LOGIN")
password = os.getenv("API_PASSWORD")
message = domain.Message(
    phone_numbers=["+12025550100"],
    text_message=domain.TextMessage(text="Hello from Python"),
)

with client.APIClient(login, password) as c:
    state = c.send(message)
```

### JWT Authentication

```python
from android_sms_gateway import client, domain

with client.APIClient(login, password) as c:
    token = c.generate_token(
        domain.TokenRequest(scopes=["messages:send", "messages:read"], ttl=3600)
    )

jwt_client = client.APIClient(None, token.access_token)
```

## 🚀 Quickstart

```python
import os

from android_sms_gateway import client, domain

message = domain.Message(
    phone_numbers=["+12025550100"],
    text_message=domain.TextMessage(text="Hello from Python"),
    with_delivery_report=True,
)

with client.APIClient(os.getenv("API_LOGIN"), os.getenv("API_PASSWORD")) as c:
    state = c.send(message)
    print(f"Message ID: {state.id}")
```

## 💻 Usage

Beyond sending, the client covers message listing and cancellation, inbox listing and refresh, device management, health checks, logs, settings (get, update, patch), webhooks, and the token lifecycle. See [android_sms_gateway/client.py](https://github.com/android-sms-gateway/client-py/blob/master/android_sms_gateway/client.py) for the complete method list with signatures and [android_sms_gateway/domain.py](https://github.com/android-sms-gateway/client-py/blob/master/android_sms_gateway/domain.py) for the domain models.

## 📖 API Reference

- [Official API Reference](https://docs.sms-gate.app/integration/api/) - endpoints, payloads, and error codes
- [Authentication Guide](https://docs.sms-gate.app/integration/authentication/) - scopes and token management
- [Client libraries overview](https://docs.sms-gate.app/integration/client-libraries/)
- [Client source](https://github.com/android-sms-gateway/client-py/blob/master/android_sms_gateway/client.py) - full method reference and examples

## 🗺️ Roadmap

- [ ] Add support for batch message sending
- [ ] Implement message scheduling
- [ ] Add webhook signature verification
- [ ] Support for custom HTTP headers
- [ ] Async context manager improvements

See the [open issues](https://github.com/android-sms-gateway/client-py/issues) for a full list of proposed features and known issues.

## 🤝 Contributing

Contributions are welcome. Open an issue to discuss major changes before submitting a pull request; PRs target the `master` branch.

## 📞 Contact

**Aleksandr Soloshenko** - admin@sms-gate.app

Project Link: [https://github.com/android-sms-gateway/client-py](https://github.com/android-sms-gateway/client-py)

## 📄 License

Distributed under the Apache License 2.0. See [LICENSE](https://github.com/android-sms-gateway/client-py/blob/master/LICENSE).

## 🙏 Acknowledgments

- [requests](https://docs.python-requests.org/) - HTTP library for sync requests
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client/server
- [httpx](https://www.python-httpx.org/) - Modern HTTP client for sync and async
- [pycryptodome](https://pycryptodome.readthedocs.io/) - Cryptographic library for encryption
- [Best README Template](https://github.com/othneildrew/Best-README-Template) - README structure inspiration

<!-- Badge references: Shields.io style=for-the-badge is mandatory -->
[contributors-shield]: https://img.shields.io/github/contributors/android-sms-gateway/client-py?style=for-the-badge
[contributors-url]: https://github.com/android-sms-gateway/client-py/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/android-sms-gateway/client-py?style=for-the-badge
[forks-url]: https://github.com/android-sms-gateway/client-py/network/members
[stars-shield]: https://img.shields.io/github/stars/android-sms-gateway/client-py?style=for-the-badge
[stars-url]: https://github.com/android-sms-gateway/client-py/stargazers
[issues-shield]: https://img.shields.io/github/issues/android-sms-gateway/client-py?style=for-the-badge
[issues-url]: https://github.com/android-sms-gateway/client-py/issues
[license-shield]: https://img.shields.io/github/license/android-sms-gateway/client-py?style=for-the-badge
[license-url]: https://github.com/android-sms-gateway/client-py/blob/master/LICENSE
[version-shield]: https://img.shields.io/pypi/v/android-sms-gateway?style=for-the-badge
[version-url]: https://pypi.org/project/android-sms-gateway/
