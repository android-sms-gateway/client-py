# 📱 SMSGate Python Client

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stars][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![PyPI Version][version-shield]][version-url]

A modern Python client for the [SMSGate](https://sms-gate.app) API: send SMS messages through your Android devices with synchronous and asynchronous interfaces, Basic or JWT authentication, and optional end-to-end encryption. See the [client libraries overview](https://docs.sms-gate.app/integration/client-libraries/) for the full ecosystem.

## 📖 About

`android-sms-gateway` is a typed Python library for the SMSGate 3rd-party API, with fully type-hinted domain models. It ships a synchronous `APIClient` and an asynchronous `AsyncAPIClient`, auto-detects the installed HTTP backend (`requests`, `aiohttp`, or `httpx`), and supports optional end-to-end message encryption via `Encryptor` (AES-256-CBC) or the device-paired `PublicKeyEncryptor` (RSA-OAEP + AES-256-GCM). Covers messages (SMS, data, and MMS), inbox (refresh, attachments), devices, webhooks, settings, logs, health probes, and the JWT token lifecycle.

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
  - [🔒 Encryption](#-encryption)
    - [Device-paired encryption](#device-paired-encryption)
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
- Optional end-to-end encryption: passphrase `Encryptor` (AES-256-CBC) or device-paired `PublicKeyEncryptor` (RSA-OAEP + AES-256-GCM, encrypt-only)
- Webhooks, devices, settings, logs, and health probes (health, liveness, readiness, startup)
- Outgoing MMS with subject, text, and base64 attachments via `MmsMessage` (E2E-encrypted when configured)
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
   export SMSGATE_LOGIN="your-login"
   export SMSGATE_PASSWORD="your-password"
   ```

3. Send your first message:
   ```python
   import os
   from android_sms_gateway import client, domain

   message = domain.Message(
       phone_numbers=["+12025550100"],
       text_message=domain.TextMessage(text="Hello from Python"),
   )

   with client.APIClient(os.getenv("SMSGATE_LOGIN"), os.getenv("SMSGATE_PASSWORD")) as c:
       state = c.send(message)
       print(f"Message ID: {state.id}")
   ```

## 🔑 Authentication

Two methods are supported: Basic authentication with account credentials, and JWT bearer tokens with scoped permissions. Pass `login=None` with a token to switch to JWT.

### Basic Authentication

```python
import os

from android_sms_gateway import client, domain

login = os.getenv("SMSGATE_LOGIN")
password = os.getenv("SMSGATE_PASSWORD")
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

## 🔒 Encryption

Optional end-to-end encryption requires the `encryption` extra (`pip install android-sms-gateway[encryption]`). Pass an encryptor via `encryptor=` to `APIClient` or `AsyncAPIClient`; outgoing message content, phone numbers, and MMS attachments are then encrypted before send.

Two encryptors are available:

- **`Encryptor(passphrase)`** — passphrase-based AES-256-CBC (PBKDF2-SHA1). Can both encrypt and decrypt, so encrypted recipient phone numbers in responses are decrypted automatically.
- **`PublicKeyEncryptor`** — device-paired RSA-OAEP + AES-256-GCM, built from the device's E2E public key. Encrypt-only: the private key never leaves the Android device, so `decrypt()` raises and encrypted recipient numbers in responses are returned unchanged.

### Device-paired encryption

```python
import base64
import hashlib

from android_sms_gateway import PublicKeyEncryptor, client, domain

PINNED_DEVICE_ID = "your-device-id"
PINNED_FINGERPRINT = "A1B2:C3D4:E5F6:7890:ABCD:EF12:3456:7890:1111:2222:3333:4444:5555:6666:7777:8888"


def key_fingerprint(public_key: str) -> str:
    digest = hashlib.sha256(base64.b64decode(public_key)).hexdigest().upper()
    return ":".join(digest[i : i + 4] for i in range(0, 64, 4))


with client.APIClient(login, password) as c:
    device = next((d for d in c.list_devices() if d.id == PINNED_DEVICE_ID), None)

if device is None:
    raise RuntimeError("Pinned device not found")

if (
    device.public_key is None
    or key_fingerprint(device.public_key) != PINNED_FINGERPRINT
):
    raise RuntimeError("Device key changed; re-verify it out of band before sending")

encryptor = PublicKeyEncryptor.from_device(device)

message = domain.Message(
    device_id=device.id,
    phone_numbers=["+12025550100"],
    text_message=domain.TextMessage(text="Hello from Python"),
)

with client.APIClient(login, password, encryptor=encryptor) as c:
    state = c.send(message)
```

The values pinned above come from the device itself (Settings → Device → Device Key): the key fingerprint, rendered as uppercase hex in 16 colon-separated groups of 4. The key returned by `list_devices()` is published through the server, so treat it as untrusted until verified: keep the pinned value stored outside the server and fail closed when changes. See the [key verification procedure](https://docs.sms-gate.app/privacy/encryption/#trust-model-and-key-verification) for details.

Rules enforced by the client:

- `from_device` raises `ValueError` if the device has no E2E public key (`public_key` / `key_version` unset).
- If the encryptor has a `device_id`, `message.device_id` must match it, otherwise `send` raises `ValueError`. `from_device` sets this ID; direct construction defaults to `None` and disables the check.
- Requesting state for an encrypted message without an encryptor set raises `ValueError`.

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
