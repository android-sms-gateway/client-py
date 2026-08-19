import dataclasses
import datetime
import typing as t

from ._utils import _parse_iso

# MMS webhook payload types


@dataclasses.dataclass(frozen=True)
class MmsReceivedPayload:
    """Payload of an mms:received event (MMS notification, not yet downloaded)."""

    message_id: str
    """The unique identifier of the message."""
    phone_number: str
    """The phone number of the sender."""
    sender: str
    """The phone number of the message sender."""
    transaction_id: str
    """Unique MMS transaction identifier."""
    content_class: str
    """MMS content classification."""
    size: int
    """Attachment size in bytes."""
    received_at: datetime.datetime
    """The timestamp when the MMS message was received."""
    recipient: t.Optional[str] = None
    """The phone number of the message recipient."""
    sim_number: t.Optional[int] = None
    """The SIM card number that received the message."""
    subject: t.Optional[str] = None
    """Message subject line."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "MmsReceivedPayload":
        """Creates an MmsReceivedPayload instance from a dictionary."""
        return cls(
            message_id=payload["messageId"],
            phone_number=payload["phoneNumber"],
            sender=payload["sender"],
            transaction_id=payload["transactionId"],
            content_class=payload["contentClass"],
            size=payload["size"],
            received_at=_parse_iso(payload["receivedAt"]),
            recipient=payload.get("recipient"),
            sim_number=payload.get("simNumber"),
            subject=payload.get("subject"),
        )


@dataclasses.dataclass(frozen=True)
class MmsDownloadedAttachment:
    """Metadata for a non-text MMS part (attachment)."""

    part_id: int
    """The _id from content://mms/part."""
    content_type: str
    """MIME type of the attachment (e.g. image/jpeg)."""
    name: t.Optional[str] = None
    """Filename of the attachment, if present."""
    data: t.Optional[str] = None
    """Base64-encoded attachment data, if available."""
    size: t.Optional[int] = None
    """Size in bytes, if known."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "MmsDownloadedAttachment":
        """Creates an MmsDownloadedAttachment instance from a dictionary."""
        return cls(
            part_id=payload["partId"],
            content_type=payload["contentType"],
            name=payload.get("name"),
            data=payload.get("data"),
            size=payload.get("size"),
        )


@dataclasses.dataclass(frozen=True)
class MmsDownloadedPayload:
    """Payload of an mms:downloaded event (fully downloaded MMS with attachments)."""

    message_id: str
    """The unique identifier of the message."""
    phone_number: str
    """The phone number of the sender."""
    sender: str
    """The phone number of the message sender."""
    attachments: t.List[MmsDownloadedAttachment]
    """Metadata for non-text MMS parts, including optional Base64 content."""
    received_at: datetime.datetime
    """The timestamp when the MMS message was received."""
    recipient: t.Optional[str] = None
    """The phone number of the message recipient."""
    sim_number: t.Optional[int] = None
    """The SIM card number that received the message."""
    subject: t.Optional[str] = None
    """Message subject line."""
    body: t.Optional[str] = None
    """Aggregated text content of the MMS message."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "MmsDownloadedPayload":
        """Creates an MmsDownloadedPayload instance from a dictionary."""
        return cls(
            message_id=payload["messageId"],
            phone_number=payload["phoneNumber"],
            sender=payload["sender"],
            attachments=[
                MmsDownloadedAttachment.from_dict(a)
                for a in payload.get("attachments", [])
            ],
            received_at=_parse_iso(payload["receivedAt"]),
            recipient=payload.get("recipient"),
            sim_number=payload.get("simNumber"),
            subject=payload.get("subject"),
            body=payload.get("body"),
        )


# SMS webhook payload types


@dataclasses.dataclass(frozen=True)
class SmsReceivedPayload:
    """Payload of an sms:received event."""

    message_id: str
    """The unique identifier of the message."""
    phone_number: str
    """The phone number of the sender."""
    sender: str
    """The phone number of the message sender."""
    message: str
    """The content of the SMS message received."""
    received_at: datetime.datetime
    """The timestamp when the SMS message was received."""
    recipient: t.Optional[str] = None
    """The phone number of the message recipient."""
    sim_number: t.Optional[int] = None
    """The SIM card number that received the message."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SmsReceivedPayload":
        """Creates an SmsReceivedPayload instance from a dictionary."""
        return cls(
            message_id=payload["messageId"],
            phone_number=payload["phoneNumber"],
            sender=payload["sender"],
            message=payload["message"],
            received_at=_parse_iso(payload["receivedAt"]),
            recipient=payload.get("recipient"),
            sim_number=payload.get("simNumber"),
        )


@dataclasses.dataclass(frozen=True)
class SmsDataReceivedPayload:
    """Payload of an sms:data-received event."""

    message_id: str
    """The unique identifier of the message."""
    phone_number: str
    """The phone number of the sender."""
    sender: str
    """The phone number of the message sender."""
    data: str
    """Base64-encoded content of the SMS message received."""
    received_at: datetime.datetime
    """The timestamp when the SMS message was received."""
    recipient: t.Optional[str] = None
    """The phone number of the message recipient."""
    sim_number: t.Optional[int] = None
    """The SIM card number that received the message."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SmsDataReceivedPayload":
        """Creates an SmsDataReceivedPayload instance from a dictionary."""
        return cls(
            message_id=payload["messageId"],
            phone_number=payload["phoneNumber"],
            sender=payload["sender"],
            data=payload["data"],
            received_at=_parse_iso(payload["receivedAt"]),
            recipient=payload.get("recipient"),
            sim_number=payload.get("simNumber"),
        )


@dataclasses.dataclass(frozen=True)
class SmsBatchReceivedPayload:
    """Payload of an sms:batch:received event."""

    messages: t.Tuple[SmsReceivedPayload, ...]
    """The ordered tuple of received SMS messages."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SmsBatchReceivedPayload":
        """Creates an SmsBatchReceivedPayload instance from a dictionary."""
        messages = payload.get("messages")
        if not isinstance(messages, (list, tuple)):
            messages = ()
        return cls(
            messages=tuple(SmsReceivedPayload.from_dict(m) for m in messages)
        )


@dataclasses.dataclass(frozen=True)
class SmsBatchDataReceivedPayload:
    """Payload of an sms:batch:data-received event."""

    messages: t.Tuple[SmsDataReceivedPayload, ...]
    """The ordered tuple of received data SMS messages."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SmsBatchDataReceivedPayload":
        """Creates an SmsBatchDataReceivedPayload instance from a dictionary."""
        messages = payload.get("messages")
        if not isinstance(messages, (list, tuple)):
            messages = ()
        return cls(
            messages=tuple(SmsDataReceivedPayload.from_dict(m) for m in messages)
        )


@dataclasses.dataclass(frozen=True)
class MmsBatchReceivedPayload:
    """Payload of an mms:batch:received event."""

    messages: t.Tuple[MmsReceivedPayload, ...]
    """The ordered tuple of received MMS messages."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "MmsBatchReceivedPayload":
        """Creates an MmsBatchReceivedPayload instance from a dictionary."""
        messages = payload.get("messages")
        if not isinstance(messages, (list, tuple)):
            messages = ()
        return cls(
            messages=tuple(MmsReceivedPayload.from_dict(m) for m in messages)
        )


@dataclasses.dataclass(frozen=True)
class MmsBatchDownloadedPayload:
    """Payload of an mms:batch:downloaded event."""

    messages: t.Tuple[MmsDownloadedPayload, ...]
    """The ordered tuple of downloaded MMS messages."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "MmsBatchDownloadedPayload":
        """Creates an MmsBatchDownloadedPayload instance from a dictionary."""
        messages = payload.get("messages")
        if not isinstance(messages, (list, tuple)):
            messages = ()
        return cls(
            messages=tuple(MmsDownloadedPayload.from_dict(m) for m in messages)
        )
