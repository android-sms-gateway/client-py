import abc
import base64
import dataclasses
import logging
import sys
import typing as t

from . import ahttp, domain, http
from .constants import DEFAULT_URL, VERSION
from .encryption import BaseEncryptor

logger = logging.getLogger(__name__)


class BaseClient(abc.ABC):
    def __init__(
        self,
        login: str,
        password: str,
        *,
        base_url: str = DEFAULT_URL,
        encryptor: t.Optional[BaseEncryptor] = None,
    ) -> None:
        credentials = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode(
            "utf-8"
        )
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "User-Agent": f"android-sms-gateway/{VERSION} (client; python {sys.version_info.major}.{sys.version_info.minor})",
        }
        self.base_url = base_url.rstrip("/")
        self.encryptor = encryptor

    def _encrypt(self, message: domain.Message) -> domain.Message:
        if self.encryptor is None:
            return message

        if message.is_encrypted:
            raise ValueError("Message is already encrypted")

        message = dataclasses.replace(
            message,
            is_encrypted=True,
            message=self.encryptor.encrypt(message.message),
            phone_numbers=[
                self.encryptor.encrypt(phone) for phone in message.phone_numbers
            ],
        )

        return message

    def _decrypt(self, state: domain.MessageState) -> domain.MessageState:
        if state.is_encrypted and self.encryptor is None:
            raise ValueError("Message is encrypted but encryptor is not set")

        if self.encryptor is None:
            return state

        return dataclasses.replace(
            state,
            recipients=[
                dataclasses.replace(
                    recipient,
                    phone_number=self.encryptor.decrypt(recipient.phone_number),
                )
                for recipient in state.recipients
            ],
            is_encrypted=False,
        )


class APIClient(BaseClient):
    def __init__(
        self,
        login: str,
        password: str,
        *,
        base_url: str = DEFAULT_URL,
        encryptor: t.Optional[BaseEncryptor] = None,
        http: t.Optional[http.HttpClient] = None,
    ) -> None:
        super().__init__(login, password, base_url=base_url, encryptor=encryptor)
        self.http = http
        self.default_http = None

    def __enter__(self):
        if self.http is not None:
            return self

        self.http = self.default_http = http.get_client().__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.default_http is None:
            return

        self.default_http.__exit__(exc_type, exc_val, exc_tb)
        self.http = self.default_http = None

    def send(self, message: domain.Message) -> domain.MessageState:
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        message = self._encrypt(message)
        return self._decrypt(
            domain.MessageState.from_dict(
                self.http.post(
                    f"{self.base_url}/message",
                    payload=message.asdict(),
                    headers=self.headers,
                )
            )
        )

    def get_state(self, _id: str) -> domain.MessageState:
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        return self._decrypt(
            domain.MessageState.from_dict(
                self.http.get(f"{self.base_url}/message/{_id}", headers=self.headers)
            )
        )

    def get_webhooks(self) -> t.List[domain.Webhook]:
        """
        Retrieves a list of all webhooks registered for the account.

        Returns:
            A list of Webhook instances.
        """
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        return [
            domain.Webhook.from_dict(webhook)
            for webhook in self.http.get(
                f"{self.base_url}/webhooks", headers=self.headers
            )
        ]

    def create_webhook(self, webhook: domain.Webhook) -> domain.Webhook:
        """
        Creates a new webhook.

        Args:
            webhook: The webhook to create.

        Returns:
            The created webhook.
        """
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        return domain.Webhook.from_dict(
            self.http.post(
                f"{self.base_url}/webhooks",
                payload=webhook.asdict(),
                headers=self.headers,
            )
        )

    def delete_webhook(self, _id: str) -> None:
        """
        Deletes a webhook.

        Args:
            _id: The ID of the webhook to delete.

        Returns:
            None
        """
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        self.http.delete(f"{self.base_url}/webhooks/{_id}", headers=self.headers)


class AsyncAPIClient(BaseClient):
    def __init__(
        self,
        login: str,
        password: str,
        *,
        base_url: str = DEFAULT_URL,
        encryptor: t.Optional[BaseEncryptor] = None,
        http_client: t.Optional[ahttp.AsyncHttpClient] = None,
    ) -> None:
        super().__init__(login, password, base_url=base_url, encryptor=encryptor)
        self.http = http_client
        self.default_http = None

    async def __aenter__(self):
        if self.http is not None:
            return self

        self.http = self.default_http = await ahttp.get_client().__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.default_http is None:
            return

        await self.default_http.__aexit__(exc_type, exc_val, exc_tb)
        self.http = self.default_http = None

    async def send(self, message: domain.Message) -> domain.MessageState:
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        message = self._encrypt(message)
        return self._decrypt(
            domain.MessageState.from_dict(
                await self.http.post(
                    f"{self.base_url}/message",
                    payload=message.asdict(),
                    headers=self.headers,
                )
            )
        )

    async def get_state(self, _id: str) -> domain.MessageState:
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        return self._decrypt(
            domain.MessageState.from_dict(
                await self.http.get(
                    f"{self.base_url}/message/{_id}", headers=self.headers
                )
            )
        )

    async def get_webhooks(self) -> t.List[domain.Webhook]:
        """
        Retrieves a list of all webhooks registered for the account.

        Returns:
            A list of Webhook instances.
        """
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        return [
            domain.Webhook.from_dict(webhook)
            for webhook in await self.http.get(
                f"{self.base_url}/webhooks", headers=self.headers
            )
        ]

    async def create_webhook(self, webhook: domain.Webhook) -> domain.Webhook:
        """
        Creates a new webhook.

        Args:
            webhook: The webhook to create.

        Returns:
            The created webhook.
        """
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        return domain.Webhook.from_dict(
            await self.http.post(
                f"{self.base_url}/webhooks",
                payload=webhook.asdict(),
                headers=self.headers,
            )
        )

    async def delete_webhook(self, _id: str) -> None:
        """
        Deletes a webhook.

        Args:
            _id: The ID of the webhook to delete.

        Returns:
            None
        """
        if self.http is None:
            raise ValueError("HTTP client not initialized")

        await self.http.delete(f"{self.base_url}/webhooks/{_id}", headers=self.headers)
