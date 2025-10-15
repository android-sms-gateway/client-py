import abc
import typing as t

from .errors import (
    error_from_status,
)


class AsyncHttpClient(t.Protocol):
    @abc.abstractmethod
    async def get(
        self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> dict: ...

    @abc.abstractmethod
    async def post(
        self, url: str, payload: dict, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> dict: ...

    @abc.abstractmethod
    async def put(
        self, url: str, payload: dict, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> dict: ...

    @abc.abstractmethod
    async def patch(
        self, url: str, payload: dict, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> dict: ...

    @abc.abstractmethod
    async def delete(
        self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
    ) -> None:
        """
        Sends a DELETE request to the specified URL.

        Args:
            url: The URL to send the DELETE request to.
            headers: Optional dictionary of HTTP headers to send with the request.

        Returns:
            None
        """

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


DEFAULT_CLIENT: t.Optional[t.Type[AsyncHttpClient]] = None


try:
    import aiohttp

    class AiohttpAsyncHttpClient(AsyncHttpClient):
        def __init__(self, session: t.Optional[aiohttp.ClientSession] = None) -> None:
            self._session = session

        async def __aenter__(self):
            if self._session is not None:
                raise ValueError("Session already initialized")

            self._session = await aiohttp.ClientSession().__aenter__()

            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self._session is None:
                return

            await self._session.close()
            self._session = None

        async def _process_response(self, response: aiohttp.ClientResponse) -> dict:
            try:
                response.raise_for_status()
                if response.status == 204:
                    return {}

                return await response.json()
            except aiohttp.ClientResponseError as e:
                # Extract error message from response if available
                error_data = {}
                try:
                    error_data = await response.json()
                except ValueError:
                    # Response is not JSON
                    pass

                # Use the error mapping to create appropriate exception
                error_message = str(e) or "HTTP request failed"
                raise error_from_status(
                    error_message, response.status, error_data
                ) from e

        async def get(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> dict:
            if self._session is None:
                raise ValueError("Session not initialized")

            async with self._session.get(url, headers=headers) as response:
                return await self._process_response(response)

        async def post(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            if self._session is None:
                raise ValueError("Session not initialized")

            async with self._session.post(
                url, headers=headers, json=payload
            ) as response:
                return await self._process_response(response)

        async def put(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            if self._session is None:
                raise ValueError("Session not initialized")

            async with self._session.put(
                url, headers=headers, json=payload
            ) as response:
                return await self._process_response(response)

        async def patch(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            if self._session is None:
                raise ValueError("Session not initialized")

            async with self._session.patch(
                url, headers=headers, json=payload
            ) as response:
                return await self._process_response(response)

        async def delete(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> None:
            if self._session is None:
                raise ValueError("Session not initialized")

            async with self._session.delete(url, headers=headers) as response:
                await self._process_response(response)

    DEFAULT_CLIENT = AiohttpAsyncHttpClient
except ImportError:
    pass

try:
    import httpx

    class HttpxAsyncHttpClient(AsyncHttpClient):
        def __init__(self, client: t.Optional[httpx.AsyncClient] = None) -> None:
            self._client = client

        async def __aenter__(self):
            if self._client is not None:
                raise ValueError("Client already initialized")

            self._client = await httpx.AsyncClient().__aenter__()

            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            if self._client is None:
                return

            await self._client.aclose()
            self._client = None

        async def _process_response(self, response: httpx.Response) -> dict:
            try:
                response.raise_for_status()
                if response.status_code == 204:
                    return {}

                return response.json()
            except httpx.HTTPStatusError as e:
                # Extract error message from response if available
                error_data = {}
                try:
                    error_data = response.json()
                except ValueError:
                    # Response is not JSON
                    pass

                # Use the error mapping to create appropriate exception
                error_message = str(e) or "HTTP request failed"
                raise error_from_status(
                    error_message, response.status_code, error_data
                ) from e

        async def get(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> dict:
            if self._client is None:
                raise ValueError("Client not initialized")

            response = await self._client.get(url, headers=headers)
            return await self._process_response(response)

        async def post(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            if self._client is None:
                raise ValueError("Client not initialized")

            response = await self._client.post(url, headers=headers, json=payload)
            return await self._process_response(response)

        async def put(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            if self._client is None:
                raise ValueError("Client not initialized")

            response = await self._client.put(url, headers=headers, json=payload)
            return await self._process_response(response)

        async def patch(
            self,
            url: str,
            payload: dict,
            *,
            headers: t.Optional[t.Dict[str, str]] = None,
        ) -> dict:
            if self._client is None:
                raise ValueError("Client not initialized")

            response = await self._client.patch(url, headers=headers, json=payload)
            return await self._process_response(response)

        async def delete(
            self, url: str, *, headers: t.Optional[t.Dict[str, str]] = None
        ) -> None:
            if self._client is None:
                raise ValueError("Client not initialized")

            response = await self._client.delete(url, headers=headers)
            await self._process_response(response)

    DEFAULT_CLIENT = HttpxAsyncHttpClient
except ImportError:
    pass


def get_client() -> AsyncHttpClient:
    if DEFAULT_CLIENT is None:
        raise ImportError("Please install aiohttp or httpx")

    return DEFAULT_CLIENT()
