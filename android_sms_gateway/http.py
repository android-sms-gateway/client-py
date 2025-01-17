import abc
import typing as t


class HttpClient(t.Protocol):
    @abc.abstractmethod
    def get(
        self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> dict: ...

    @abc.abstractmethod
    def post(
        self, url: str, payload: dict, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> dict: ...

    @abc.abstractmethod
    def delete(self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None) -> None:
        """
        Sends a DELETE request to the specified URL.

        Args:
            url: The URL to send the DELETE request to.
            headers: Optional dictionary of HTTP headers to send with the request.

        Returns:
            None
        """

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


DEFAULT_CLIENT: t.Optional[t.Type[HttpClient]] = None

try:
    import requests

    class RequestsHttpClient(HttpClient):
        def __init__(self, session: t.Optional[requests.Session] = None) -> None:
            self._session = session

        def __enter__(self):
            if self._session is not None:
                raise ValueError("Session already initialized")

            self._session = requests.Session().__enter__()

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._session is None:
                return

            self._session.close()
            self._session = None

        def get(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> dict:
            if self._session is None:
                raise ValueError("Session not initialized")

            return self._process_response(self._session.get(url, headers=headers))

        def post(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            if self._session is None:
                raise ValueError("Session not initialized")

            return self._process_response(
                self._session.post(url, headers=headers, json=payload)
            )

        def delete(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> None:
            if self._session is None:
                raise ValueError("Session not initialized")

            self._session.delete(url, headers=headers).raise_for_status()

        def _process_response(self, response: requests.Response) -> dict:
            response.raise_for_status()
            return response.json()

    DEFAULT_CLIENT = RequestsHttpClient
except ImportError:
    pass

try:
    import httpx

    class HttpxHttpClient(HttpClient):
        def __init__(self, client: t.Optional[httpx.Client] = None) -> None:
            self._client = client

        def __enter__(self):
            if self._client is not None:
                raise ValueError("Client already initialized")

            self._client = httpx.Client().__enter__()

            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self._client is None:
                return

            self._client.close()
            self._client = None

        def get(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> dict:
            if self._client is None:
                raise ValueError("Client not initialized")

            return self._client.get(url, headers=headers).raise_for_status().json()

        def post(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            if self._client is None:
                raise ValueError("Client not initialized")

            return (
                self._client.post(url, headers=headers, json=payload)
                .raise_for_status()
                .json()
            )

        def delete(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> None:
            if self._client is None:
                raise ValueError("Client not initialized")

            self._client.delete(url, headers=headers).raise_for_status()

    DEFAULT_CLIENT = HttpxHttpClient
except ImportError:
    pass


def get_client() -> HttpClient:
    if DEFAULT_CLIENT is None:
        raise ImportError("Please install requests or httpx")

    return DEFAULT_CLIENT()
