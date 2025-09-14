import enum


class ProcessState(enum.Enum):
    Pending = "Pending"
    Processed = "Processed"
    Sent = "Sent"
    Delivered = "Delivered"
    Failed = "Failed"


class WebhookEvent(enum.Enum):
    """
    Webhook events that can be sent by the server.
    """

    SMS_RECEIVED = "sms:received"
    """Triggered when an SMS is received."""

    SMS_SENT = "sms:sent"
    """Triggered when an SMS is sent."""

    SMS_DELIVERED = "sms:delivered"
    """Triggered when an SMS is delivered."""

    SMS_FAILED = "sms:failed"
    """Triggered when an SMS processing fails."""

    SYSTEM_PING = "system:ping"
    """Triggered when the device pings the server."""


class MessagePriority(enum.IntEnum):
    """Priority levels for messages."""

    MINIMUM = -128
    """Minimum priority level."""

    DEFAULT = 0
    """Default priority level."""

    BYPASS_THRESHOLD = 100
    """Priority level to bypass limits and delays."""

    MAXIMUM = 127
    """Maximum priority level."""
