import dataclasses
import typing as t

from .enums import ProcessState, WebhookEvent


def snake_to_camel(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


@dataclasses.dataclass(frozen=True)
class Message:
    message: str
    phone_numbers: t.List[str]
    with_delivery_report: bool = True
    is_encrypted: bool = False

    id: t.Optional[str] = None
    ttl: t.Optional[int] = None
    sim_number: t.Optional[int] = None

    def asdict(self) -> t.Dict[str, t.Any]:
        return {
            snake_to_camel(field.name): getattr(self, field.name)
            for field in dataclasses.fields(self)
            if getattr(self, field.name) is not None
        }


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
