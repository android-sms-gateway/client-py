# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.3.0] - Unreleased

### Added

- **`created_at` field in `MessageState`** — message state now includes a `created_at` timestamp indicating when the message was created
  ```python
  state = client.get_state(message_id)
  print(f"Created at: {state.created_at}")
  ```

### Changed

- Unified README style and structure for better readability

## [4.2.0] - 2026-08-19

### Added

- **Batch webhook support** — webhooks can now deliver multiple messages in a single batch
  ```python
  from android_sms_gateway import domain

  webhook = domain.Webhook(
      url="https://your-server.com/webhook",
      events=[domain.WebhookEvent.SMS_RECEIVED],
      delivery=domain.WebhookDelivery.BATCH,
  )
  client.create_webhook(webhook)
  ```

## [4.1.0] - 2026-08-01

### Added

- **Sort parameter for `get_messages`** — sort messages by timestamp or other fields
- **MMS attachment download** — download MMS attachments from inbox messages
- **Message cancellation** — cancel pending messages before they are sent

### Changed

- Improved error handling with typed exceptions

## [4.0.0] - 2026-07-15

### Added

- **JWT authentication** — generate, refresh, and revoke JWT tokens with scoped permissions
- **Webhook management** — create, list, and delete webhooks programmatically
- **Device management** — list and remove registered devices
- **Settings management** — get, update, and patch device settings
- **Health checks** — liveness, readiness, and startup probes
- **Log retrieval** — fetch system logs with time range filtering

### Changed

- Migrated from `requests` to protocol-based HTTP abstraction
- Added support for `httpx` and `aiohttp` backends
- Improved type hints and domain models

### Removed

- Deprecated legacy API methods

## [3.3.0] - 2026-06-01

### Added

- **End-to-end encryption** — optional message encryption using AES-256-CBC
- **Inbox refresh** — refresh device inboxes with webhook delivery

### Changed

- Improved error messages and documentation

## [3.2.0] - 2026-05-15

### Added

- **Async support** — `AsyncAPIClient` for asynchronous operations
- **Context managers** — both sync and async clients support context managers

### Changed

- Refactored HTTP client architecture

## [3.0.0] - 2026-04-01

### Added

- **Message listing** — list messages with filtering and pagination
- **Delivery reports** — track message delivery status
- **Message priority** — set message priority levels

### Changed

- Breaking changes to domain model structure

## [2.0.0] - 2026-03-01

### Added

- **Basic API client** — send SMS messages through Android devices
- **Device selection** — choose specific SIM cards for sending

### Changed

- Initial public release

## [1.0.0] - 2026-02-01

### Added

- Initial release with core functionality