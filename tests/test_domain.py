import pytest
import datetime

from android_sms_gateway.enums import WebhookEvent, MessagePriority
from android_sms_gateway.domain import (
    MessageState,
    RecipientState,
    Webhook,
    Message,
    TextMessage,
    DataMessage,
)


# Test for successful instantiation from a dictionary
def test_message_state_from_dict():
    payload = {
        "id": "123",
        "state": "Pending",
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"},
            {"phoneNumber": "456", "state": "Pending"},
        ],
        "isHashed": True,
        "isEncrypted": False,
    }

    message_state = MessageState.from_dict(payload)
    assert message_state.id == payload["id"]
    assert message_state.state.name == payload["state"]
    assert all(
        isinstance(recipient, RecipientState) for recipient in message_state.recipients
    )
    assert len(message_state.recipients) == len(payload["recipients"])
    assert message_state.is_hashed == payload["isHashed"]
    assert message_state.is_encrypted == payload["isEncrypted"]


# Test for backward compatibility
def test_message_state_from_dict_backwards_compatibility():
    payload = {
        "id": "123",
        "state": "Pending",
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"},
            {"phoneNumber": "456", "state": "Pending"},
        ],
    }

    message_state = MessageState.from_dict(payload)
    assert message_state.id == payload["id"]
    assert message_state.state.name == payload["state"]
    assert all(
        isinstance(recipient, RecipientState) for recipient in message_state.recipients
    )
    assert len(message_state.recipients) == len(payload["recipients"])
    assert message_state.is_hashed is False
    assert message_state.is_encrypted is False


# Test for handling missing fields
def test_message_state_from_dict_missing_fields():
    incomplete_payload = {
        "id": "123",
        # 'state' is missing
        "recipients": [
            {"phoneNumber": "123", "state": "Pending"}
        ],  # Assume one recipient is enough to test
        "isHashed": True,
        "isEncrypted": False,
    }

    with pytest.raises(KeyError):
        MessageState.from_dict(incomplete_payload)


# Test for handling incorrect types
def test_message_state_from_dict_incorrect_types():
    incorrect_payload = {
        "id": 123,  # Should be a string
        "state": 42,  # Should be a string that can be converted to a ProcessState
        "recipients": "Alice, Bob",  # Should be a list of dictionaries
        "isHashed": "yes",  # Should be a boolean
        "isEncrypted": "no",  # Should be a boolean
    }

    with pytest.raises(
        Exception
    ):  # Replace Exception with the specific exception you expect
        MessageState.from_dict(incorrect_payload)


def test_webhook_from_dict():
    """
    Tests that a Webhook instance can be successfully instantiated from a dictionary
    representation of a webhook.
    """
    payload = {
        "id": "webhook_123",
        "url": "https://example.com/webhook",
        "event": "sms:received",
    }

    webhook = Webhook.from_dict(payload)

    assert webhook.id == payload["id"]
    assert webhook.url == payload["url"]
    assert webhook.event == WebhookEvent(payload["event"])


def test_webhook_asdict():
    """
    Tests that a Webhook instance can be successfully converted to a dictionary
    representation and that the fields match the expected values.

    This test ensures that the asdict method of the Webhook class returns a dictionary
    with the correct keys and values.
    """
    webhook = Webhook(
        id="webhook_123",
        url="https://example.com/webhook",
        event=WebhookEvent.SMS_RECEIVED,
    )

    expected_dict = {
        "id": "webhook_123",
        "url": "https://example.com/webhook",
        "event": "sms:received",
    }

    assert webhook.asdict() == expected_dict

    webhook = Webhook(
        id=None,
        url="https://example.com/webhook",
        event=WebhookEvent.SMS_RECEIVED,
    )

    expected_dict = {
        "id": None,
        "url": "https://example.com/webhook",
        "event": "sms:received",
    }

    assert webhook.asdict() == expected_dict


@pytest.mark.parametrize(
    "message_content,phone_numbers,with_delivery_report,is_encrypted,id,ttl,sim_number,priority,expected",
    [
        (
            "Hello, world!",
            ["123", "456"],
            True,
            False,
            "msg_123",
            300,
            1,
            MessagePriority.BYPASS_THRESHOLD,
            {
                "textMessage": {"text": "Hello, world!"},
                "phoneNumbers": ["123", "456"],
                "withDeliveryReport": True,
                "isEncrypted": False,
                "id": "msg_123",
                "ttl": 300,
                "simNumber": 1,
                "priority": 100,
            },
        ),
        (
            "Hello, world!",
            ["123", "456"],
            True,
            False,
            None,
            None,
            None,
            None,
            {
                "textMessage": {"text": "Hello, world!"},
                "phoneNumbers": ["123", "456"],
                "withDeliveryReport": True,
                "isEncrypted": False,
            },
        ),
        (
            "Hello, world!",
            ["123", "456"],
            True,
            False,
            "msg_123",
            None,
            1,
            None,
            {
                "textMessage": {"text": "Hello, world!"},
                "phoneNumbers": ["123", "456"],
                "withDeliveryReport": True,
                "isEncrypted": False,
                "id": "msg_123",
                "simNumber": 1,
            },
        ),
        (
            "Hello, world!",
            ["123", "456"],
            True,
            False,
            "msg_123",
            None,
            None,
            MessagePriority.DEFAULT,
            {
                "textMessage": {"text": "Hello, world!"},
                "phoneNumbers": ["123", "456"],
                "withDeliveryReport": True,
                "isEncrypted": False,
                "id": "msg_123",
                "priority": 0,
            },
        ),
        (
            "Hi",
            ["555"],
            True,
            False,
            None,
            None,
            None,
            MessagePriority.MINIMUM,
            {
                "textMessage": {"text": "Hi"},
                "phoneNumbers": ["555"],
                "withDeliveryReport": True,
                "isEncrypted": False,
                "priority": -128,
            },
        ),
    ],
)
def test_message_asdict(
    message_content,
    phone_numbers,
    with_delivery_report,
    is_encrypted,
    id,
    ttl,
    sim_number,
    priority,
    expected,
):
    """
    Tests that a Message instance can be successfully converted to a dictionary
    representation with camelCase keys and that only non-None fields are included.
    Uses parametrized testing to cover multiple scenarios.
    """
    message = Message(
        text_message=TextMessage(text=message_content),
        phone_numbers=phone_numbers,
        with_delivery_report=with_delivery_report,
        is_encrypted=is_encrypted,
        id=id,
        ttl=ttl,
        sim_number=sim_number,
        priority=priority,
    )

    assert message.asdict() == expected


# Test for Message with data_message instead of text_message
def test_message_with_data_message_only():
    """Test creating a message with data_message only"""
    data_msg = DataMessage(data="base64encodeddata", port=1234)
    message = Message(
        phone_numbers=["123", "456"],
        data_message=data_msg,
        with_delivery_report=True,
        is_encrypted=False,
    )

    assert message.data_message == data_msg
    assert message.text_message is None


def test_message_serialization_with_data_message():
    """Test serialization includes data_message"""
    data_msg = DataMessage(data="base64encodeddata", port=1234)
    message = Message(
        phone_numbers=["123", "456"],
        data_message=data_msg,
        with_delivery_report=True,
        is_encrypted=False,
        id="msg_123",
        device_id="device_001",
    )

    expected_dict = {
        "dataMessage": {"data": "base64encodeddata", "port": 1234},
        "phoneNumbers": ["123", "456"],
        "withDeliveryReport": True,
        "isEncrypted": False,
        "id": "msg_123",
        "deviceId": "device_001",
    }

    assert message.asdict() == expected_dict


# Test for Message with both ttl and valid_until (should raise ValueError)
def test_message_with_both_ttl_and_valid_until_raises_error():
    """Test that providing both ttl and valid_until raises ValueError"""
    text_msg = TextMessage(text="Hello, world!")

    with pytest.raises(ValueError, match="ttl and valid_until are mutually exclusive"):
        Message(
            phone_numbers=["123", "456"],
            text_message=text_msg,
            ttl=300,
            valid_until=datetime.datetime.now() + datetime.timedelta(seconds=600),
        )


def test_message_with_ttl_only():
    """Test that providing only ttl works correctly"""
    text_msg = TextMessage(text="Hello, world!")
    message = Message(
        phone_numbers=["123", "456"],
        text_message=text_msg,
        ttl=300,
    )

    assert message.ttl == 300
    assert message.valid_until is None
    assert "ttl" in message.asdict()
    assert "validUntil" not in message.asdict()


def test_message_with_valid_until_only():
    """Test that providing only valid_until works correctly"""
    text_msg = TextMessage(text="Hello, world!")
    valid_until_time = datetime.datetime.now() + datetime.timedelta(seconds=600)
    message = Message(
        phone_numbers=["123", "456"],
        text_message=text_msg,
        valid_until=valid_until_time,
    )

    assert message.valid_until == valid_until_time
    assert message.ttl is None
    assert "validUntil" in message.asdict()
    assert "ttl" not in message.asdict()


# Test content property for both text and data messages, plus error case
def test_message_content_property_with_text_message():
    """Test content property returns text_message when text is set"""
    text_msg = TextMessage(text="Hello, world!")
    message = Message(
        phone_numbers=["123", "456"],
        text_message=text_msg,
    )

    assert message.content == "Hello, world!"


def test_message_content_property_with_data_message():
    """Test content property returns data_message when data is set"""
    data_msg = DataMessage(data="base64encodeddata", port=1234)
    message = Message(
        phone_numbers=["123", "456"],
        data_message=data_msg,
    )

    assert message.content == "base64encodeddata"


def test_message_without_text_or_data_raises_error():
    """Test that creating message without text or data raises appropriate error"""
    message = Message(phone_numbers=["123", "456"])

    with pytest.raises(ValueError, match="Message has no content"):
        _ = message.content


# Test serialization including device_id and valid_until
def test_message_serialization_with_device_id():
    """Test serialization includes device_id when present"""
    text_msg = TextMessage(text="Hello, world!")
    message = Message(
        phone_numbers=["123", "456"],
        text_message=text_msg,
        device_id="device_001",
    )

    assert "deviceId" in message.asdict()
    assert message.asdict()["deviceId"] == "device_001"


def test_message_serialization_with_valid_until():
    """Test serialization includes valid_until when present"""
    text_msg = TextMessage(text="Hello, world!")
    valid_until_time = datetime.datetime.now() + datetime.timedelta(seconds=600)
    message = Message(
        phone_numbers=["123", "456"],
        text_message=text_msg,
        valid_until=valid_until_time,
    )

    assert "validUntil" in message.asdict()
    assert message.asdict()["validUntil"] == valid_until_time.isoformat()


def test_message_serialization_with_ttl():
    """Test serialization includes ttl when present"""
    text_msg = TextMessage(text="Hello, world!")
    message = Message(
        phone_numbers=["123", "456"],
        text_message=text_msg,
        ttl=300,
    )

    assert "ttl" in message.asdict()
    assert message.asdict()["ttl"] == 300


def test_message_serialization_format_for_text_message():
    """Test serialization format for text message"""
    text_msg = TextMessage(text="Hello, world!")
    message = Message(
        phone_numbers=["123", "456"],
        text_message=text_msg,
        with_delivery_report=True,
        is_encrypted=False,
        id="msg_123",
        device_id="device_001",
        ttl=300,
        sim_number=1,
        priority=MessagePriority.BYPASS_THRESHOLD,
    )

    expected_dict = {
        "textMessage": {"text": "Hello, world!"},
        "phoneNumbers": ["123", "456"],
        "withDeliveryReport": True,
        "isEncrypted": False,
        "id": "msg_123",
        "deviceId": "device_001",
        "ttl": 300,
        "simNumber": 1,
        "priority": 100,
    }

    assert message.asdict() == expected_dict


def test_message_serialization_format_for_data_message():
    """Test serialization format for data message"""
    data_msg = DataMessage(data="base64encodeddata", port=1234)
    message = Message(
        phone_numbers=["123", "456"],
        data_message=data_msg,
        with_delivery_report=True,
        is_encrypted=False,
        id="msg_123",
        device_id="device_001",
        ttl=300,
        sim_number=1,
        priority=MessagePriority.BYPASS_THRESHOLD,
    )

    expected_dict = {
        "dataMessage": {"data": "base64encodeddata", "port": 1234},
        "phoneNumbers": ["123", "456"],
        "withDeliveryReport": True,
        "isEncrypted": False,
        "id": "msg_123",
        "deviceId": "device_001",
        "ttl": 300,
        "simNumber": 1,
        "priority": 100,
    }

    assert message.asdict() == expected_dict
