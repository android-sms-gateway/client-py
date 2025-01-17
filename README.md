# SMS Gateway for Android™ Python API Client

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/blob/main/LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/capcom6/android-sms-gateway-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/issues)
[![GitHub Stars](https://img.shields.io/github/stars/capcom6/android-sms-gateway-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/capcom6/android-sms-gateway-py.svg?style=for-the-badge)](https://github.com/android-sms-gateway/client-py/network)
[![PyPI Version](https://img.shields.io/pypi/v/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![Python Version](https://img.shields.io/pypi/pyversions/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)
[![Downloads](https://img.shields.io/pypi/dm/android-sms-gateway.svg?style=for-the-badge)](https://pypi.org/project/android-sms-gateway/)

This is a Python client library for interfacing with the [SMS Gateway for Android](https://sms-gate.app) API.

## Requirements

- Python >= 3.7
- One of the following packages:
    - [requests](https://pypi.org/project/requests/)
    - [aiohttp](https://pypi.org/project/aiohttp/)
    - [httpx](https://pypi.org/project/httpx/)

Optional:

- [pycryptodome](https://pypi.org/project/pycryptodome/) - end-to-end encryption support

## Installation

```bash
pip install android_sms_gateway
```

You can also install it with the preferred HTTP client:

```bash
pip install android_sms_gateway[requests]
pip install android_sms_gateway[aiohttp]
pip install android_sms_gateway[httpx]
```

With encrypted messages support:

```bash
pip install android_sms_gateway[encryption]
```

## Quickstart

Here's an example of using the client:

```python
import asyncio
import os

from android_sms_gateway import client, domain, Encryptor

login = os.getenv("ANDROID_SMS_GATEWAY_LOGIN")
password = os.getenv("ANDROID_SMS_GATEWAY_PASSWORD")
# encryptor = Encryptor('passphrase') # for end-to-end encryption, see https://sms-gate.app/privacy/encryption/

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

## Client

There are two client classes: `APIClient` and `AsyncAPIClient`. The
`APIClient` is synchronous and the `AsyncAPIClient` is asynchronous. Both
implement the same interface and can be used as context managers.

### Methods

There are two groups of methods:

**Messages**

- `send(message: domain.Message) -> domain.MessageState`: Send a new SMS message.
- `get_state(_id: str) -> domain.MessageState`: Retrieve the state of a previously sent message by its ID.

**Webhooks**

- `get_webhooks() -> list[domain.Webhook]`: Retrieve a list of all webhooks registered for the account.
- `create_webhook(webhook: domain.Webhook) -> domain.Webhook`: Create a new webhook.
- `delete_webhook(_id: str)`: Delete a webhook by its ID.

## HTTP Client

The API clients abstract away the HTTP client used to make requests. The library includes support for some popular HTTP clients and tries to discover them automatically:

- [requests](https://pypi.org/project/requests/) - `APIClient` only
- [aiohttp](https://pypi.org/project/aiohttp/) - `AsyncAPIClient` only
- [httpx](https://pypi.org/project/httpx/) - `APIClient` and `AsyncAPIClient`

You can also implement your own HTTP client that conforms to the `http.HttpClient` or `ahttp.HttpClient` protocol.

# Contributing

Contributions are welcome! Please submit a pull request or create an issue for anything you'd like to add or change.

# License

This library is open-sourced software licensed under the [Apache-2.0 license](LICENSE).
