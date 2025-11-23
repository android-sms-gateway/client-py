import pytest
from unittest.mock import AsyncMock, MagicMock

from android_sms_gateway.client import APIClient, AsyncAPIClient
from android_sms_gateway.constants import DEFAULT_URL
from android_sms_gateway.domain import TokenRequest, TokenResponse
from android_sms_gateway.http import RequestsHttpClient


def test_basic_auth_initialization():
    """Test that the client can be initialized with Basic Auth (backward compatibility)."""
    with (
        RequestsHttpClient() as h,
        APIClient(
            "test_login",
            "test_password",
            base_url=DEFAULT_URL,
            http=h,
        ) as client,
    ):
        # Check that the Authorization header is set correctly
        assert "Authorization" in client.headers
        assert client.headers["Authorization"].startswith("Basic ")
        assert client.headers["Content-Type"] == "application/json"
        assert "User-Agent" in client.headers


def test_jwt_auth_initialization():
    """Test that the client can be initialized with JWT token."""
    with (
        RequestsHttpClient() as h,
        APIClient(
            login=None,
            password="test_jwt_token",
            base_url=DEFAULT_URL,
            http=h,
        ) as client,
    ):
        # Check that the Authorization header is set correctly
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test_jwt_token"
        assert client.headers["Content-Type"] == "application/json"
        assert "User-Agent" in client.headers


def test_async_basic_auth_initialization():
    """Test that the async client can be initialized with Basic Auth (backward compatibility)."""
    client = AsyncAPIClient(
        "test_login",
        "test_password",
        base_url=DEFAULT_URL,
    )
    # Check that the Authorization header is set correctly
    assert "Authorization" in client.headers
    assert client.headers["Authorization"].startswith("Basic ")
    assert client.headers["Content-Type"] == "application/json"
    assert "User-Agent" in client.headers


def test_async_jwt_auth_initialization():
    """Test that the async client can be initialized with JWT token."""
    client = AsyncAPIClient(
        login=None,
        password="test_jwt_token",
        base_url=DEFAULT_URL,
    )
    # Check that the Authorization header is set correctly
    assert "Authorization" in client.headers
    assert client.headers["Authorization"] == "Bearer test_jwt_token"
    assert client.headers["Content-Type"] == "application/json"
    assert "User-Agent" in client.headers


def test_missing_credentials_error():
    """Test that an error is raised when neither login/password nor jwt_token is provided."""
    with pytest.raises(
        ValueError,
        match="Either login and password or token must be provided",
    ):
        APIClient(None, "")


def test_missing_password_error():
    """Test that an error is raised when login is provided but password is missing."""
    with pytest.raises(
        ValueError,
        match="Either login and password or token must be provided",
    ):
        APIClient(login="test_login", password="")


def test_async_missing_credentials_error():
    """Test that an error is raised when neither login/password nor jwt_token is provided for async client."""
    with pytest.raises(
        ValueError,
        match="Either login and password or token must be provided",
    ):
        AsyncAPIClient(None, "")


def test_generate_token():
    """Test that the client can generate a new JWT token."""
    mock_http = MagicMock()
    mock_http.post.return_value = {
        "accessToken": "test_access_token",
        "tokenType": "Bearer",
        "id": "test_token_id",
        "expiresAt": "2023-12-31T23:59:59Z",
    }

    token_request = TokenRequest(scopes=["sms:send", "sms:read"], ttl=3600)

    with APIClient(
        login=None,
        password="initial_token",
        base_url=DEFAULT_URL,
        http=mock_http,
    ) as client:
        response = client.generate_token(token_request)

        # Verify the response
        assert isinstance(response, TokenResponse)
        assert response.access_token == "test_access_token"
        assert response.token_type == "Bearer"
        assert response.id == "test_token_id"
        assert response.expires_at == "2023-12-31T23:59:59Z"

        # Verify the HTTP call
        mock_http.post.assert_called_once_with(
            f"{DEFAULT_URL}/auth/token",
            payload=token_request.asdict(),
            headers=client.headers,
        )


def test_revoke_token():
    """Test that the client can revoke a JWT token."""
    mock_http = MagicMock()
    mock_http.delete.return_value = None

    with APIClient(
        login=None,
        password="initial_token",
        base_url=DEFAULT_URL,
        http=mock_http,
    ) as client:
        client.revoke_token("test_token_id")

        # Verify the HTTP call
        mock_http.delete.assert_called_once_with(
            f"{DEFAULT_URL}/auth/token/test_token_id",
            headers=client.headers,
        )


@pytest.mark.asyncio
async def test_async_generate_token():
    """Test that the async client can generate a new JWT token."""
    mock_http = AsyncMock()
    mock_http.post.return_value = {
        "accessToken": "test_access_token",
        "tokenType": "Bearer",
        "id": "test_token_id",
        "expiresAt": "2023-12-31T23:59:59Z",
    }

    token_request = TokenRequest(scopes=["sms:send", "sms:read"], ttl=3600)

    async with AsyncAPIClient(
        login=None,
        password="initial_token",
        base_url=DEFAULT_URL,
        http_client=mock_http,
    ) as client:
        response = await client.generate_token(token_request)

        # Verify the response
        assert isinstance(response, TokenResponse)
        assert response.access_token == "test_access_token"
        assert response.token_type == "Bearer"
        assert response.id == "test_token_id"
        assert response.expires_at == "2023-12-31T23:59:59Z"

        # Verify the HTTP call
        mock_http.post.assert_called_once_with(
            f"{DEFAULT_URL}/auth/token",
            payload=token_request.asdict(),
            headers=client.headers,
        )


@pytest.mark.asyncio
async def test_async_revoke_token():
    """Test that the async client can revoke a JWT token."""
    mock_http = AsyncMock()
    mock_http.delete.return_value = None

    async with AsyncAPIClient(
        login=None,
        password="initial_token",
        base_url=DEFAULT_URL,
        http_client=mock_http,
    ) as client:
        await client.revoke_token("test_token_id")

        # Verify the HTTP call
        mock_http.delete.assert_called_once_with(
            f"{DEFAULT_URL}/auth/token/test_token_id",
            headers=client.headers,
        )
