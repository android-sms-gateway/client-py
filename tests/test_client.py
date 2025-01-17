import os
import pytest
from requests import HTTPError

from android_sms_gateway.client import APIClient
from android_sms_gateway.constants import DEFAULT_URL
from android_sms_gateway.domain import Webhook
from android_sms_gateway.enums import WebhookEvent
from android_sms_gateway.http import RequestsHttpClient


@pytest.fixture
def client():
    """
    A fixture providing an instance of `APIClient` for use in tests.

    The client is created using the values of the following environment variables:

    - `API_LOGIN` (defaults to `"test"`)
    - `API_PASSWORD` (defaults to `"test"`)
    - `API_BASE_URL` (defaults to `constants.DEFAULT_URL`)

    The client is yielded from the fixture, and automatically closed when the
    test is finished.

    :yields: An instance of `APIClient`.
    """
    with RequestsHttpClient() as h, APIClient(
        os.environ.get("API_LOGIN") or "test",
        os.environ.get("API_PASSWORD") or "test",
        base_url=os.environ.get("API_BASE_URL") or DEFAULT_URL,
        http=h,
    ) as c:
        yield c


@pytest.mark.skipif(
    not all(
        [
            os.environ.get("API_LOGIN"),
            os.environ.get("API_PASSWORD"),
        ]
    ),
    reason="API credentials are not set in the environment variables",
)
class TestAPIClient:
    def test_webhook_create(self, client: APIClient):
        """
        Tests that a webhook can be successfully created using the client.

        It creates a webhook, and then asserts that the created webhook matches the
        expected values.

        :param client: An instance of `APIClient`.
        """
        item = Webhook(
            id="webhook_123",
            url="https://example.com/webhook",
            event=WebhookEvent.SMS_RECEIVED,
        )

        created = client.create_webhook(item)

        assert created.id == "webhook_123"
        assert created.url == "https://example.com/webhook"
        assert created.event == WebhookEvent.SMS_RECEIVED

    def test_webhook_create_invalid_url(self, client: APIClient):
        """
        Tests that attempting to create a webhook with an invalid URL raises an
        `HTTPError`.

        The test creates a webhook with an invalid URL, and then asserts that an
        `HTTPError` is raised.

        :param client: An instance of `APIClient`.
        """
        with pytest.raises(HTTPError):
            client.create_webhook(
                Webhook(None, url="not_a_url", event=WebhookEvent.SMS_RECEIVED)
            )

    def test_webhook_get(self, client: APIClient):
        """
        Tests that the `get_webhooks` method retrieves a non-empty list of webhooks
        and that it contains a webhook with the expected ID, URL, and event type.

        :param client: An instance of `APIClient`.
        """

        webhooks = client.get_webhooks()

        assert len(webhooks) > 0

        assert any(
            [
                webhook.id == "webhook_123"
                and webhook.url == "https://example.com/webhook"
                and webhook.event == WebhookEvent.SMS_RECEIVED
                for webhook in webhooks
            ]
        )

    def test_webhook_delete(self, client: APIClient):
        """
        Tests that a webhook can be successfully deleted using the client.

        It deletes a webhook with a specific ID and then asserts that the list of
        webhooks does not contain a webhook with that ID.

        :param client: An instance of `APIClient`.
        """

        client.delete_webhook("webhook_123")

        webhooks = client.get_webhooks()

        assert not any([webhook.id == "webhook_123" for webhook in webhooks])
