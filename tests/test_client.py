import asyncio
import datetime
import os
import pytest

from android_sms_gateway.client import APIClient, AsyncAPIClient
from android_sms_gateway.constants import DEFAULT_URL
from android_sms_gateway.domain import (
    Webhook,
    InboxRefreshRequest,
    MessagesExportRequest,
)
from android_sms_gateway.enums import WebhookDelivery, WebhookEvent
from android_sms_gateway.http import RequestsHttpClient
from android_sms_gateway import errors


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
        `errors.APIError`.

        The test creates a webhook with an invalid URL, and then asserts that an
        `errors.APIError` is raised.

        :param client: An instance of `APIClient`.
        """
        with pytest.raises(errors.APIError):
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


class StubHttpClient:
    """
    A minimal HttpClient protocol stub that records post calls and returns a
    canned response, allowing client tests to run without a live server or
    API credentials.
    """

    def __init__(self, response):
        self.response = response
        self.calls = []

    def post(self, url, payload, *, headers=None):
        self.calls.append(
            {"url": url, "payload": payload, "headers": headers}
        )
        return self.response


class StubAsyncHttpClient:
    """
    A minimal AsyncHttpClient protocol stub that records post calls and
    returns a canned response, allowing async client tests to run without a
    live server or API credentials.
    """

    def __init__(self, response):
        self.response = response
        self.calls = []

    async def post(self, url, payload, *, headers=None):
        self.calls.append(
            {"url": url, "payload": payload, "headers": headers}
        )
        return self.response


def _refresh_request():
    return InboxRefreshRequest(
        since=datetime.datetime(2026, 8, 1, 10, 0, 0),
        until=datetime.datetime(2026, 8, 2, 10, 0, 0),
        device_id="device_1",
        webhook_delivery=WebhookDelivery.INDIVIDUAL,
    )


def _export_request():
    return MessagesExportRequest(
        device_id="device_1",
        since=datetime.datetime(2026, 8, 1, 10, 0, 0),
        until=datetime.datetime(2026, 8, 2, 10, 0, 0),
    )


def test_refresh_inbox_posts_request_to_inbox_refresh():
    """
    Tests that refresh_inbox POSTs the request payload to /inbox/refresh
    and returns the response body.
    """
    stub = StubHttpClient({"status": "ok"})
    client = APIClient(
        "user", "pass", base_url="https://example.com", http=stub
    )
    request = _refresh_request()

    result = client.refresh_inbox(request)

    assert result == {"status": "ok"}
    assert len(stub.calls) == 1
    assert stub.calls[0]["url"] == "https://example.com/inbox/refresh"
    assert stub.calls[0]["payload"] == request.asdict()
    assert stub.calls[0]["headers"]["Authorization"]


def test_async_refresh_inbox_posts_request_to_inbox_refresh():
    """
    Tests that the async refresh_inbox POSTs the request payload to
    /inbox/refresh and returns the response body.
    """
    stub = StubAsyncHttpClient({"status": "ok"})
    client = AsyncAPIClient(
        "user", "pass", base_url="https://example.com", http_client=stub
    )
    request = _refresh_request()

    result = asyncio.run(client.refresh_inbox(request))

    assert result == {"status": "ok"}
    assert len(stub.calls) == 1
    assert stub.calls[0]["url"] == "https://example.com/inbox/refresh"
    assert stub.calls[0]["payload"] == request.asdict()


class RaisingStubHttpClient(StubHttpClient):
    """
    A StubHttpClient variant whose post raises the configured error,
    mirroring an HTTP client surfacing a non-202 error status.
    """

    def post(self, url, payload, *, headers=None):
        super().post(url, payload, headers=headers)
        raise self.response


class RaisingStubAsyncHttpClient(StubAsyncHttpClient):
    """
    A StubAsyncHttpClient variant whose post raises the configured error,
    mirroring an HTTP client surfacing a non-202 error status.
    """

    async def post(self, url, payload, *, headers=None):
        self.calls.append(
            {"url": url, "payload": payload, "headers": headers}
        )
        raise self.response


def test_refresh_inbox_handles_202_empty_body():
    """
    Tests that refresh_inbox returns the empty dict produced by the HTTP
    layer for a 202 Accepted response with an empty body, without decoding
    errors.
    """
    stub = StubHttpClient({})
    client = APIClient(
        "user", "pass", base_url="https://example.com", http=stub
    )

    result = client.refresh_inbox(_refresh_request())

    assert result == {}
    assert len(stub.calls) == 1
    assert stub.calls[0]["url"] == "https://example.com/inbox/refresh"


def test_async_refresh_inbox_handles_202_empty_body():
    """
    Tests that the async refresh_inbox returns the empty dict produced by
    the HTTP layer for a 202 Accepted response with an empty body, without
    decoding errors.
    """
    stub = StubAsyncHttpClient({})
    client = AsyncAPIClient(
        "user", "pass", base_url="https://example.com", http_client=stub
    )

    result = asyncio.run(client.refresh_inbox(_refresh_request()))

    assert result == {}
    assert len(stub.calls) == 1
    assert stub.calls[0]["url"] == "https://example.com/inbox/refresh"


def test_refresh_inbox_propagates_non_202_error_status():
    """
    Tests that refresh_inbox propagates the API error raised by the HTTP
    layer for a non-202 error status instead of swallowing it.
    """
    stub = RaisingStubHttpClient(errors.InternalServerError("boom", status_code=500))
    client = APIClient(
        "user", "pass", base_url="https://example.com", http=stub
    )

    with pytest.raises(errors.InternalServerError):
        client.refresh_inbox(_refresh_request())


def test_async_refresh_inbox_propagates_non_202_error_status():
    """
    Tests that the async refresh_inbox propagates the API error raised by
    the HTTP layer for a non-202 error status instead of swallowing it.
    """
    stub = RaisingStubAsyncHttpClient(errors.InternalServerError("boom", status_code=500))
    client = AsyncAPIClient(
        "user", "pass", base_url="https://example.com", http_client=stub
    )

    with pytest.raises(errors.InternalServerError):
        asyncio.run(client.refresh_inbox(_refresh_request()))


def test_export_inbox_posts_request_to_messages_inbox_export():
    """
    Regression lock: export_inbox must POST to the deprecated server alias
    /messages/inbox/export (not /inbox/export) and return the response body.
    """
    stub = StubHttpClient({"status": "ok"})
    client = APIClient(
        "user", "pass", base_url="https://example.com", http=stub
    )
    request = _export_request()

    result = client.export_inbox(request)

    assert result == {"status": "ok"}
    assert len(stub.calls) == 1
    assert stub.calls[0]["url"] == "https://example.com/messages/inbox/export"
    assert stub.calls[0]["url"] != "https://example.com/inbox/export"
    assert stub.calls[0]["payload"] == request.asdict()


def test_async_export_inbox_posts_request_to_messages_inbox_export():
    """
    Regression lock: async export_inbox must POST to the deprecated server
    alias /messages/inbox/export (not /inbox/export) and return the response
    body.
    """
    stub = StubAsyncHttpClient({"status": "ok"})
    client = AsyncAPIClient(
        "user", "pass", base_url="https://example.com", http_client=stub
    )
    request = _export_request()

    result = asyncio.run(client.export_inbox(request))

    assert result == {"status": "ok"}
    assert len(stub.calls) == 1
    assert stub.calls[0]["url"] == "https://example.com/messages/inbox/export"
    assert stub.calls[0]["payload"] == request.asdict()
