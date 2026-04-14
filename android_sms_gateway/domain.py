import base64
import dataclasses
import datetime
import enum
import typing as t

from .enums import (
    ProcessState,
    WebhookEvent,
    MessagePriority,
    LimitPeriod,
    SimSelectionMode,
    MessagesProcessingOrder,
    HealthStatus,
    LogEntryPriority,
)


def _parse_iso(value: t.Optional[str]) -> t.Optional[datetime.datetime]:
    """Parse an ISO 8601 timestamp string to a datetime object.

    Args:
        value: An ISO 8601 timestamp string (e.g., "2024-01-01T12:00:00Z") or None.

    Returns:
        A datetime object or None if value is None.
    """
    if value is None:
        return None
    return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))


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
    device_id: t.Optional[str] = None
    states: t.Optional[t.Dict[str, str]] = None

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "MessageState":
        return cls(
            id=payload["id"],
            device_id=payload.get("deviceId"),
            state=ProcessState(payload["state"]),
            recipients=[
                RecipientState.from_dict(recipient)
                for recipient in payload["recipients"]
            ],
            is_hashed=payload.get("isHashed", False),
            is_encrypted=payload.get("isEncrypted", False),
            states=payload.get("states"),
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
    device_id: t.Optional[str] = None
    """The unique identifier of the device the webhook is associated with."""

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
            device_id=payload.get("deviceId"),
        )

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the webhook.

        Returns:
            A dictionary containing the webhook's data.
        """
        result: t.Dict[str, t.Any] = {
            "id": self.id,
            "url": self.url,
            "event": self.event.value,
        }
        if self.device_id is not None:
            result["deviceId"] = self.device_id
        return result


@dataclasses.dataclass(frozen=True)
class Device:
    """Represents a device."""

    id: str
    """The unique identifier of the device."""
    name: str
    """The name of the device."""
    created_at: t.Optional[datetime.datetime] = None
    """The timestamp when the device was created."""
    updated_at: t.Optional[datetime.datetime] = None
    """The timestamp when the device was last updated."""
    deleted_at: t.Optional[datetime.datetime] = None
    """The timestamp when the device was deleted."""
    last_seen: t.Optional[datetime.datetime] = None
    """The timestamp when the device was last seen."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "Device":
        """Creates a Device instance from a dictionary."""
        return cls(
            id=payload["id"],
            name=payload["name"],
            created_at=_parse_iso(payload.get("createdAt")),
            updated_at=_parse_iso(payload.get("updatedAt")),
            deleted_at=_parse_iso(payload.get("deletedAt")),
            last_seen=_parse_iso(payload.get("lastSeen")),
        )


@dataclasses.dataclass(frozen=True)
class ErrorResponse:
    """Represents an error response from the API."""

    code: int
    """The error code."""
    message: str
    """The error message."""
    data: t.Optional[t.Any] = None
    """Additional error context."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "ErrorResponse":
        """Creates an ErrorResponse instance from a dictionary."""
        return cls(
            code=payload["code"],
            message=payload["message"],
            data=payload.get("data"),
        )


@dataclasses.dataclass(frozen=True)
class TokenRequest:
    """Represents a request to generate a new JWT token."""

    scopes: t.List[str]
    """List of scopes for the token."""
    ttl: t.Optional[int] = None
    """Time to live for the token in seconds."""

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the token request.

        Returns:
            A dictionary containing the token request data.
        """
        result: t.Dict[str, t.Any] = {
            "scopes": self.scopes,
        }
        if self.ttl is not None:
            result["ttl"] = self.ttl
        return result


@dataclasses.dataclass(frozen=True)
class TokenResponse:
    """Represents a response when generating a new JWT token."""

    access_token: str
    """The JWT access token."""
    token_type: str
    """The type of the token (e.g., 'Bearer')."""
    id: str
    """The unique identifier of the token (jti)."""
    expires_at: str
    """The expiration time of the token in ISO format."""
    refresh_token: t.Optional[str] = None
    """The refresh token."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "TokenResponse":
        """Creates a TokenResponse instance from a dictionary.

        Args:
            payload: A dictionary containing the token response data.

        Returns:
            A TokenResponse instance.
        """
        return cls(
            access_token=payload["accessToken"],
            token_type=payload["tokenType"],
            id=payload["id"],
            expires_at=payload["expiresAt"],
            refresh_token=payload.get("refreshToken"),
        )


# Settings classes


@dataclasses.dataclass(frozen=True)
class SettingsGateway:
    """Gateway settings."""

    cloud_url: t.Optional[str] = None
    """The URL of the cloud server."""
    private_token: t.Optional[str] = None
    """The auth token for the private server."""
    notification_channel: t.Optional[str] = None
    """The way device receives notifications (AUTO, SSE_ONLY)."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SettingsGateway":
        """Creates a SettingsGateway instance from a dictionary."""
        return cls(
            cloud_url=payload.get("cloud_url"),
            private_token=payload.get("private_token"),
            notification_channel=payload.get("notification_channel"),
        )

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the settings."""
        result: t.Dict[str, t.Any] = {}
        if self.cloud_url is not None:
            result["cloud_url"] = self.cloud_url
        if self.private_token is not None:
            result["private_token"] = self.private_token
        if self.notification_channel is not None:
            result["notification_channel"] = self.notification_channel
        return result


@dataclasses.dataclass(frozen=True)
class SettingsEncryption:
    """Encryption settings."""

    passphrase: t.Optional[str] = None
    """The encryption passphrase."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SettingsEncryption":
        """Creates a SettingsEncryption instance from a dictionary."""
        return cls(
            passphrase=payload.get("passphrase"),
        )

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the settings."""
        result: t.Dict[str, t.Any] = {}
        if self.passphrase is not None:
            result["passphrase"] = self.passphrase
        return result


@dataclasses.dataclass(frozen=True)
class SettingsMessages:
    """Message handling settings."""

    limit_period: t.Optional[LimitPeriod] = None
    """The period for message sending limits."""
    limit_value: t.Optional[int] = None
    """The maximum number of messages allowed per limit period."""
    log_lifetime_days: t.Optional[int] = None
    """The number of days to retain message logs."""
    processing_order: t.Optional[MessagesProcessingOrder] = None
    """The order in which messages are processed."""
    send_interval_max: t.Optional[int] = None
    """The maximum interval between message sends (in seconds)."""
    send_interval_min: t.Optional[int] = None
    """The minimum interval between message sends (in seconds)."""
    sim_selection_mode: t.Optional[SimSelectionMode] = None
    """How SIM cards are selected for sending messages."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SettingsMessages":
        """Creates a SettingsMessages instance from a dictionary.

        Args:
            payload: A dictionary containing the settings data.

        Returns:
            A SettingsMessages instance.
        """
        # Convert enum fields from strings to enum members
        limit_period = payload.get("limit_period")
        if limit_period is not None and isinstance(limit_period, str):
            limit_period = LimitPeriod(limit_period)

        processing_order = payload.get("processing_order")
        if processing_order is not None and isinstance(processing_order, str):
            processing_order = MessagesProcessingOrder(processing_order)

        sim_selection_mode = payload.get("sim_selection_mode")
        if sim_selection_mode is not None and isinstance(sim_selection_mode, str):
            sim_selection_mode = SimSelectionMode(sim_selection_mode)

        return cls(
            limit_period=limit_period,
            limit_value=payload.get("limit_value"),
            log_lifetime_days=payload.get("log_lifetime_days"),
            processing_order=processing_order,
            send_interval_max=payload.get("send_interval_max"),
            send_interval_min=payload.get("send_interval_min"),
            sim_selection_mode=sim_selection_mode,
        )

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the settings."""
        result: t.Dict[str, t.Any] = {}
        if self.limit_period is not None:
            result["limit_period"] = self.limit_period.value
        if self.limit_value is not None:
            result["limit_value"] = self.limit_value
        if self.log_lifetime_days is not None:
            result["log_lifetime_days"] = self.log_lifetime_days
        if self.processing_order is not None:
            result["processing_order"] = self.processing_order.value
        if self.send_interval_max is not None:
            result["send_interval_max"] = self.send_interval_max
        if self.send_interval_min is not None:
            result["send_interval_min"] = self.send_interval_min
        if self.sim_selection_mode is not None:
            result["sim_selection_mode"] = self.sim_selection_mode.value
        return result


@dataclasses.dataclass(frozen=True)
class SettingsLogs:
    """Logging settings."""

    lifetime_days: t.Optional[int] = None
    """The number of days to retain logs."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SettingsLogs":
        """Creates a SettingsLogs instance from a dictionary."""
        return cls(
            lifetime_days=payload.get("lifetime_days"),
        )

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the settings."""
        result: t.Dict[str, t.Any] = {}
        if self.lifetime_days is not None:
            result["lifetime_days"] = self.lifetime_days
        return result


@dataclasses.dataclass(frozen=True)
class SettingsPing:
    """Ping settings."""

    interval_seconds: t.Optional[int] = None
    """The interval between ping requests (in seconds)."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SettingsPing":
        """Creates a SettingsPing instance from a dictionary."""
        return cls(
            interval_seconds=payload.get("interval_seconds"),
        )

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the settings."""
        result: t.Dict[str, t.Any] = {}
        if self.interval_seconds is not None:
            result["interval_seconds"] = self.interval_seconds
        return result


@dataclasses.dataclass(frozen=True)
class SettingsWebhooks:
    """Webhook settings."""

    retry_count: t.Optional[int] = None
    """The number of times to retry failed webhook deliveries."""
    signing_key: t.Optional[str] = None
    """The secret key used for signing webhook payloads."""
    internet_required: t.Optional[bool] = None
    """Whether internet access is required for webhooks."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "SettingsWebhooks":
        """Creates a SettingsWebhooks instance from a dictionary."""
        return cls(
            retry_count=payload.get("retry_count"),
            signing_key=payload.get("signing_key"),
            internet_required=payload.get("internet_required"),
        )

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the settings."""
        result: t.Dict[str, t.Any] = {}
        if self.retry_count is not None:
            result["retry_count"] = self.retry_count
        if self.signing_key is not None:
            result["signing_key"] = self.signing_key
        if self.internet_required is not None:
            result["internet_required"] = self.internet_required
        return result


@dataclasses.dataclass(frozen=True)
class DeviceSettings:
    """Device settings."""

    gateway: t.Optional[SettingsGateway] = None
    """Gateway settings."""
    encryption: t.Optional[SettingsEncryption] = None
    """Encryption settings."""
    messages: t.Optional[SettingsMessages] = None
    """Message handling settings."""
    logs: t.Optional[SettingsLogs] = None
    """Logging settings."""
    ping: t.Optional[SettingsPing] = None
    """Ping settings."""
    webhooks: t.Optional[SettingsWebhooks] = None
    """Webhook settings."""

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the settings."""
        result: t.Dict[str, t.Any] = {}
        if self.gateway is not None:
            result["gateway"] = self.gateway.asdict()
        if self.encryption is not None:
            result["encryption"] = self.encryption.asdict()
        if self.messages is not None:
            result["messages"] = self.messages.asdict()
        if self.logs is not None:
            result["logs"] = self.logs.asdict()
        if self.ping is not None:
            result["ping"] = self.ping.asdict()
        if self.webhooks is not None:
            result["webhooks"] = self.webhooks.asdict()
        return result

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "DeviceSettings":
        """Creates a DeviceSettings instance from a dictionary.

        Args:
            payload: A dictionary containing the settings data.

        Returns:
            A DeviceSettings instance.
        """
        gateway = None
        if "gateway" in payload:
            gateway = SettingsGateway.from_dict(payload["gateway"])

        encryption = None
        if "encryption" in payload:
            encryption = SettingsEncryption.from_dict(payload["encryption"])

        messages = None
        if "messages" in payload:
            messages = SettingsMessages.from_dict(payload["messages"])

        logs = None
        if "logs" in payload:
            logs = SettingsLogs.from_dict(payload["logs"])

        ping = None
        if "ping" in payload:
            ping = SettingsPing.from_dict(payload["ping"])

        webhooks = None
        if "webhooks" in payload:
            webhooks = SettingsWebhooks.from_dict(payload["webhooks"])

        return cls(
            gateway=gateway,
            encryption=encryption,
            messages=messages,
            logs=logs,
            ping=ping,
            webhooks=webhooks,
        )


# Health check classes


@dataclasses.dataclass(frozen=True)
class HealthCheck:
    """Represents a health check."""

    status: HealthStatus
    """The status of the check."""
    description: t.Optional[str] = None
    """A human-readable description of the check."""
    observed_value: t.Optional[int] = None
    """The observed value of the check."""
    observed_unit: t.Optional[str] = None
    """The unit of measurement for the observed value."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "HealthCheck":
        """Creates a HealthCheck instance from a dictionary.

        Args:
            payload: A dictionary containing the health check data.

        Returns:
            A HealthCheck instance.
        """
        return cls(
            status=HealthStatus(payload["status"]),
            description=payload.get("description"),
            observed_value=payload.get("observedValue"),
            observed_unit=payload.get("observedUnit"),
        )


@dataclasses.dataclass(frozen=True)
class HealthResponse:
    """Represents a health check response."""

    status: HealthStatus
    """The overall status of the application."""
    version: t.Optional[str] = None
    """Version of the application."""
    release_id: t.Optional[int] = None
    """Release ID of the application."""
    checks: t.Optional[t.Dict[str, HealthCheck]] = None
    """A map of check names to their respective details."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "HealthResponse":
        """Creates a HealthResponse instance from a dictionary.

        Args:
            payload: A dictionary containing the health response data.

        Returns:
            A HealthResponse instance.
        """
        checks = None
        if "checks" in payload:
            checks = {
                name: HealthCheck.from_dict(check_data)
                for name, check_data in payload["checks"].items()
            }

        return cls(
            status=HealthStatus(payload["status"]),
            version=payload.get("version"),
            release_id=payload.get("releaseId"),
            checks=checks,
        )


# Log entry class


@dataclasses.dataclass(frozen=True)
class LogEntry:
    """Represents a log entry."""

    id: int
    """A unique identifier for the log entry."""
    created_at: datetime.datetime
    """The timestamp when this log entry was created."""
    message: str
    """A message describing the log event."""
    priority: LogEntryPriority
    """The priority level of the log entry."""
    module: t.Optional[str] = None
    """The module or component of the system that generated the log entry."""
    context: t.Optional[t.Dict[str, t.Any]] = None
    """Additional context information related to the log entry."""

    @classmethod
    def from_dict(cls, payload: t.Dict[str, t.Any]) -> "LogEntry":
        """Creates a LogEntry instance from a dictionary.

        Args:
            payload: A dictionary containing the log entry data.

        Returns:
            A LogEntry instance.
        """
        return cls(
            id=payload["id"],
            created_at=_parse_iso(payload["createdAt"]),
            message=payload["message"],
            priority=LogEntryPriority(payload["priority"]),
            module=payload.get("module"),
            context=payload.get("context"),
        )


# Messages export request


@dataclasses.dataclass(frozen=True)
class MessagesExportRequest:
    """Represents a request to export inbox messages."""

    device_id: str
    """The ID of the device to export messages for."""
    since: datetime.datetime
    """The start of the time range to export."""
    until: datetime.datetime
    """The end of the time range to export."""

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the request.

        Returns:
            A dictionary containing the request data.
        """
        return {
            "deviceId": self.device_id,
            "since": self.since.isoformat(),
            "until": self.until.isoformat(),
        }


# Messages query request


@dataclasses.dataclass(frozen=True, kw_only=True)
class MessagesQueryFilter:
    """Filter parameters for message queries."""

    from_: t.Optional[datetime.datetime] = None
    """Start date in RFC3339 format."""
    to: t.Optional[datetime.datetime] = None
    """End date in RFC3339 format."""
    state: t.Optional[str] = None
    """Filter messages by processing state."""
    device_id: t.Optional[str] = None
    """Filter by device ID."""

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the query parameters.

        Returns:
            A dictionary containing the query parameters.
        """
        params: t.Dict[str, t.Any] = {}

        if self.from_ is not None:
            params["from"] = self.from_.isoformat()
        if self.to is not None:
            params["to"] = self.to.isoformat()
        if self.state is not None:
            params["state"] = self.state
        if self.device_id is not None:
            params["deviceId"] = self.device_id

        return params


@dataclasses.dataclass(frozen=True, kw_only=True)
class QueryPagination:
    """Pagination parameters for queries."""

    limit: t.Optional[int] = None
    """Pagination limit."""
    offset: t.Optional[int] = None
    """Pagination offset."""

    def asdict(self) -> t.Dict[str, t.Any]:
        """Returns a dictionary representation of the query parameters.

        Returns:
            A dictionary containing the query parameters.
        """
        params: t.Dict[str, t.Any] = {}

        # Add pagination parameters
        if self.limit is not None:
            params["limit"] = self.limit
        if self.offset is not None:
            params["offset"] = self.offset

        return params
