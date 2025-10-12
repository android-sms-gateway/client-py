import typing as t


class APIError(Exception):
    """Base class for API exceptions."""

    def __init__(
        self,
        message: str,
        status_code: t.Optional[int] = None,
        response: t.Optional[dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class BadRequestError(APIError):
    """400 - Bad Request"""


class UnauthorizedError(APIError):
    """401 - Unauthorized"""


class ForbiddenError(APIError):
    """403 - Forbidden"""


class NotFoundError(APIError):
    """404 - Not Found"""


class InternalServerError(APIError):
    """500 - Internal Server Error"""


class ServiceUnavailableError(APIError):
    """503 - Service Unavailable"""


class GatewayTimeoutError(APIError):
    """504 - Gateway Timeout"""


_ERROR_MAP = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    500: InternalServerError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}


def error_from_status(
    message: str, status: int, response: t.Optional[dict] = None
) -> APIError:
    """Factory function to map HTTP status codes to appropriate APIError subclasses.

    Args:
        message: Error message
        status: HTTP status code
        response: Optional response data

    Returns:
        Appropriate APIError subclass or APIError as fallback
    """
    return _ERROR_MAP.get(status, APIError)(
        message, status_code=status, response=response
    )
