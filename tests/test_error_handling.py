from unittest.mock import Mock

import aiohttp
import httpx
import pytest
import requests

from android_sms_gateway.ahttp import AiohttpAsyncHttpClient, HttpxAsyncHttpClient
from android_sms_gateway.errors import (
    APIError,
    BadRequestError,
    ForbiddenError,
    GatewayTimeoutError,
    InternalServerError,
    NotFoundError,
    ServiceUnavailableError,
    UnauthorizedError,
    error_from_status,
)
from android_sms_gateway.http import HttpxHttpClient, RequestsHttpClient


class TestErrorFromStatus:
    """Test the error_from_status factory function."""

    def test_maps_400_to_bad_request_error(self):
        """Test that status 400 maps to BadRequestError."""
        error = error_from_status("Bad request", 400, {"error": "bad request"})
        assert isinstance(error, BadRequestError)
        assert error.status_code == 400
        assert error.response == {"error": "bad request"}

    def test_maps_401_to_unauthorized_error(self):
        """Test that status 401 maps to UnauthorizedError."""
        error = error_from_status("Unauthorized", 401)
        assert isinstance(error, UnauthorizedError)
        assert error.status_code == 401

    def test_maps_403_to_forbidden_error(self):
        """Test that status 403 maps to ForbiddenError."""
        error = error_from_status("Forbidden", 403)
        assert isinstance(error, ForbiddenError)
        assert error.status_code == 403

    def test_maps_404_to_not_found_error(self):
        """Test that status 404 maps to NotFoundError."""
        error = error_from_status("Not found", 404)
        assert isinstance(error, NotFoundError)
        assert error.status_code == 404

    def test_maps_500_to_internal_server_error(self):
        """Test that status 500 maps to InternalServerError."""
        error = error_from_status("Internal server error", 500)
        assert isinstance(error, InternalServerError)
        assert error.status_code == 500

    def test_maps_503_to_service_unavailable_error(self):
        """Test that status 503 maps to ServiceUnavailableError."""
        error = error_from_status("Service unavailable", 503)
        assert isinstance(error, ServiceUnavailableError)
        assert error.status_code == 503

    def test_maps_504_to_gateway_timeout_error(self):
        """Test that status 504 maps to GatewayTimeoutError."""
        error = error_from_status("Gateway timeout", 504)
        assert isinstance(error, GatewayTimeoutError)
        assert error.status_code == 504

    def test_unknown_status_maps_to_api_error(self):
        """Test that unknown status codes map to APIError."""
        error = error_from_status("Unknown error", 418)
        assert isinstance(error, APIError)
        assert error.status_code == 418

    def test_default_error_message(self):
        """Test that default error message is used when not provided."""
        error = error_from_status("", 400)
        assert str(error) == ""


class TestRequestsHttpClientErrorHandling:
    """Test error handling in RequestsHttpClient."""

    def test_raises_bad_request_error_for_400(self):
        """Test that BadRequestError is raised for 400 status."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Client Error"
        )
        mock_response.json.return_value = {"error": "bad request"}

        client = RequestsHttpClient()

        with pytest.raises(BadRequestError) as exc_info:
            client._process_response(mock_response)

        assert exc_info.value.status_code == 400
        assert exc_info.value.response == {"error": "bad request"}

    def test_raises_not_found_error_for_404(self):
        """Test that NotFoundError is raised for 404 status."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Not Found"
        )
        mock_response.json.return_value = {"error": "not found"}

        client = RequestsHttpClient()

        with pytest.raises(NotFoundError) as exc_info:
            client._process_response(mock_response)

        assert exc_info.value.status_code == 404
        assert exc_info.value.response == {"error": "not found"}

    def test_raises_api_error_for_unknown_status(self):
        """Test that APIError is raised for unknown status codes."""
        mock_response = Mock()
        mock_response.status_code = 418
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "418 I'm a teapot"
        )

        client = RequestsHttpClient()

        with pytest.raises(APIError) as exc_info:
            client._process_response(mock_response)

        assert exc_info.value.status_code == 418


class TestHttpxHttpClientErrorHandling:
    """Test error handling in HttpxHttpClient."""

    def test_raises_bad_request_error_for_400(self):
        """Test that BadRequestError is raised for 400 status."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "400 Client Error", request=Mock(), response=mock_response
        )
        mock_response.json.return_value = {"error": "bad request"}

        client = HttpxHttpClient()

        with pytest.raises(BadRequestError) as exc_info:
            client._process_response(mock_response)

        assert exc_info.value.status_code == 400
        assert exc_info.value.response == {"error": "bad request"}

    def test_raises_not_found_error_for_404(self):
        """Test that NotFoundError is raised for 404 status."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )
        mock_response.json.return_value = {"error": "not found"}

        client = HttpxHttpClient()

        with pytest.raises(NotFoundError) as exc_info:
            client._process_response(mock_response)

        assert exc_info.value.status_code == 404
        assert exc_info.value.response == {"error": "not found"}


class TestAiohttpAsyncHttpClientErrorHandling:
    """Test error handling in AiohttpAsyncHttpClient."""

    @pytest.mark.asyncio
    async def test_raises_bad_request_error_for_400(self):
        """Test that BadRequestError is raised for 400 status."""
        mock_response = Mock()
        mock_response.status = 400
        mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=Mock(), history=(), status=400, message="400 Client Error"
        )
        mock_response.json.return_value = {"error": "bad request"}

        client = AiohttpAsyncHttpClient()

        with pytest.raises(BadRequestError) as exc_info:
            await client._process_response(mock_response)

        assert exc_info.value.status_code == 400
        assert exc_info.value.response == {"error": "bad request"}

    @pytest.mark.asyncio
    async def test_raises_not_found_error_for_404(self):
        """Test that NotFoundError is raised for 404 status."""
        mock_response = Mock()
        mock_response.status = 404
        mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=Mock(), history=(), status=404, message="404 Not Found"
        )
        mock_response.json.return_value = {"error": "not found"}

        client = AiohttpAsyncHttpClient()

        with pytest.raises(NotFoundError) as exc_info:
            await client._process_response(mock_response)

        assert exc_info.value.status_code == 404
        assert exc_info.value.response == {"error": "not found"}


class TestHttpxAsyncHttpClientErrorHandling:
    """Test error handling in HttpxAsyncHttpClient."""

    @pytest.mark.asyncio
    async def test_raises_bad_request_error_for_400(self):
        """Test that BadRequestError is raised for 400 status."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "400 Client Error", request=Mock(), response=mock_response
        )
        mock_response.json.return_value = {"error": "bad request"}

        client = HttpxAsyncHttpClient()

        with pytest.raises(BadRequestError) as exc_info:
            await client._process_response(mock_response)

        assert exc_info.value.status_code == 400
        assert exc_info.value.response == {"error": "bad request"}

    @pytest.mark.asyncio
    async def test_raises_not_found_error_for_404(self):
        """Test that NotFoundError is raised for 404 status."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )
        mock_response.json.return_value = {"error": "not found"}

        client = HttpxAsyncHttpClient()

        with pytest.raises(NotFoundError) as exc_info:
            await client._process_response(mock_response)

        assert exc_info.value.status_code == 404
        assert exc_info.value.response == {"error": "not found"}
