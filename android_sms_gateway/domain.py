import base64
import dataclasses
import datetime
import enum
import typing as t

from .enums import ProcessState, WebhookEvent, MessagePriority


def snake_to_camel(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


@dataclasses.dataclass(frozen=True, kw_only=True)
class Message:
    """
    Represents an SMS message.

    Attributes:
        phone_numbers (List[str]): Recipients (phone numbers).
        text_message (Optional[TextMessage]): Text message.
        data_message (Optional[DataMessage]): Data message.
        priority (Optional[MessagePriority]): Priority.
        sim_number (Optional[int]): SIM card number (1-3), if not set - default SIM will be used.
        with_delivery_report (bool): With delivery report.
        is_encrypted (bool): Is encrypted.
        ttl (Optional[int]): Time to live in seconds (conflicts with `validUntil`).
        valid_until (Optional[datetime.datetime]): Valid until (conflicts with `ttl`).
        id (Optional[str]): ID (if not set - will be generated).
        device_id (Optional[str]): Optional device ID for explicit selection.
    """

    phone_numbers: t.List[str]
    text_message: t.Optional["TextMessage"] = None
    data_message: t.Optional["DataMessage"] = None

    priority: t.Optional[MessagePriority] = None
    sim_number: t.Optional[int] = None
    with_delivery_report: bool = True
    is_encrypted: bool = False

    ttl: t.Optional[int] = None
    valid_until: t.Optional[datetime.datetime] = None

    id: t.Optional[str] = None
    device_id: t.Optional[str] = None

    def __post_init__(self):
        if self.ttl is not None and self.valid_until is not None:
            raise ValueError("ttl and valid_until are mutually exclusive")

    @property
    def content(self) -> str:
        if self.text_message:
            return self.text_message.text
        if self.data_message:
            return self.data_message.data
        raise ValueError("Message has no content")

    def asdict(self) -> t.Dict[str, t.Any]:
        """
        Returns a dictionary representation of the message.

        Returns:
            Dict[str, Any]: A dictionary representation of the message.
        """

        def _serialize(value: t.Any) -> t.Any:
            if hasattr(value, "asdict"):
                return value.asdict()
            if isinstance(value, datetime.datetime):
                return value.isoformat()
            if isinstance(value, enum.Enum):
                return value.value
            return value

        return {
            snake_to_camel(f.name): _serialize(getattr(self, f.name))
            for f in dataclasses.fields(self)
            if getattr(self, f.name) is not None
        }


@dataclasses.dataclass(frozen=True)
class DataMessage:
    """
    Represents a data message.

    Attributes:
        data (str): Base64-encoded payload.
        port (int): Destination port.
    """

    data: str
    port: int

    def asdict(self) -> t.Dict[str, t.Any]:
        return {
            "data": self.data,
            "port": self.port,
        }

    @classmethod
    def with_bytes(cls, data: bytes, port: int) -> "DataMessage":
        return cls(
            data=base64.b64encode(data).decode("utf-8"),
            port=port,
        )

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "DataMessage":
        """Creates a DataMessage instance from a dictionary.

        Args:
            payload: A dictionary containing the data message's data.

        Returns:
            A DataMessage instance.
        """
        return cls(
            data=payload["data"],
            port=payload["port"],
        )


@dataclasses.dataclass(frozen=True)
class TextMessage:
    """
    Represents a text message.

    Attributes:
        text (str): Message text.
    """

    text: str

    def asdict(self) -> t.Dict[str, t.Any]:
        return {
            "text": self.text,
        }

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "TextMessage":
        """Creates a TextMessage instance from a dictionary.

        Args:
            payload: A dictionary containing the text message's data.

        Returns:
            A TextMessage instance.
        """
        return cls(
            text=payload["text"],
        )


@dataclasses.dataclass(frozen=True)
class RecipientState:
    phone_number: str
    state: ProcessState
    error: t.Optional[str]

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "RecipientState":
        return cls(
            phone_number=payload["phoneNumber"],
            state=ProcessState(payload["state"]),
            error=payload.get("error"),
        )


@dataclasses.dataclass(frozen=True)
class MessageState:
    id: str
    state: ProcessState
    recipients: t.List[RecipientState]
    is_hashed: bool
    is_encrypted: bool

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "MessageState":
        return cls(
            id=payload["id"],
            state=ProcessState(payload["state"]),
            recipients=[
                RecipientState.from_dict(recipient)
                for recipient in payload["recipients"]
            ],
            is_hashed=payload.get("isHashed", False),
            is_encrypted=payload.get("isEncrypted", False),
        )


@dataclasses.dataclass(frozen=True)
class Webhook:
    """A webhook configuration."""

    id: t.Optional[str]
    """The unique identifier of the webhook."""
    url: str
    """The URL the webhook will be sent to."""
    event: WebhookEvent
    """The type of event the webhook is triggered for."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "Webhook":
        """Creates a Webhook instance from a dictionary.

        Args:
            payload: A dictionary containing the webhook's data.

        Returns:
            A Webhook instance.
        """
        return cls(
            id=payload.get("id"),
            url=payload["url"],
            event=WebhookEvent(payload["event"]),
        )

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the webhook.

        Returns:
            A dictionary containing the webhook's data.
        """
        return {
            "id": self.id,
            "url": self.url,
            "event": self.event.value,
        }


@dataclasses.dataclass(frozen=True)
class Device:
    """Represents a device."""

    id: str
    """The unique identifier of the device."""
    name: str
    """The name of the device."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "Device":
        """Creates a Device instance from a dictionary."""
        return cls(
            id=payload["id"],
            name=payload["name"],
        )


@dataclasses.dataclass(frozen=True)
class ErrorResponse:
    """Represents an error response from the API."""

    code: int
    """The error code."""
    message: str
    """The error message."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "ErrorResponse":
        """Creates an ErrorResponse instance from a dictionary."""
        return cls(
            code=payload["code"],
            message=payload["message"],
        )
