import pytest
from android_sms_gateway.client import APIClient, AsyncAPIClient
from android_sms_gateway.constants import DEFAULT_URL
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
            password_or_token="test_jwt_token",
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
        password_or_token="test_jwt_token",
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
        APIClient(login="test_login", password_or_token="")


def test_async_missing_credentials_error():
    """Test that an error is raised when neither login/password nor jwt_token is provided for async client."""
    with pytest.raises(
        ValueError,
        match="Either login and password or token must be provided",
    ):
        AsyncAPIClient(None, "")
