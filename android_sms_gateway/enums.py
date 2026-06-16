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

    SMS_DATA_RECEIVED = "sms:data-received"
    """Triggered when a data SMS is received."""

    SMS_SENT = "sms:sent"
    """Triggered when an SMS is sent."""

    SMS_DELIVERED = "sms:delivered"
    """Triggered when an SMS is delivered."""

    SMS_FAILED = "sms:failed"
    """Triggered when an SMS processing fails."""

    SYSTEM_PING = "system:ping"
    """Triggered when the device pings the server."""

    MMS_RECEIVED = "mms:received"
    """Triggered when an MMS is received."""

    MMS_DOWNLOADED = "mms:downloaded"
    """Triggered when an MMS is downloaded."""

    APP_STARTED = "app:started"
    """Triggered when the application is started."""


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


class LimitPeriod(enum.Enum):
    """Period for message sending limits."""

    DISABLED = "Disabled"
    """Limits are disabled."""

    PER_MINUTE = "PerMinute"
    """Limit is applied per minute."""

    PER_HOUR = "PerHour"
    """Limit is applied per hour."""

    PER_DAY = "PerDay"
    """Limit is applied per day."""


class SimSelectionMode(enum.Enum):
    """Mode for selecting SIM cards for sending messages."""

    OS_DEFAULT = "OSDefault"
    """Use the OS default selection."""

    ROUND_ROBIN = "RoundRobin"
    """Round-robin selection across SIM cards."""

    RANDOM = "Random"
    """Random selection across SIM cards."""


class MessagesProcessingOrder(enum.Enum):
    """Order in which messages are processed."""

    LIFO = "LIFO"
    """Last in, first out."""

    FIFO = "FIFO"
    """First in, first out."""


class HealthStatus(enum.Enum):
    """Health check status."""

    PASS = "pass"
    """Check passed."""

    WARN = "warn"
    """Check passed with warnings."""

    FAIL = "fail"
    """Check failed."""


class LogEntryPriority(enum.Enum):
    """Priority level of a log entry."""

    DEBUG = "DEBUG"
    """Debug level."""

    INFO = "INFO"
    """Info level."""

    WARN = "WARN"
    """Warning level."""

    ERROR = "ERROR"
    """Error level."""
