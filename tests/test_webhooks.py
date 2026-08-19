import datetime

import pytest

from android_sms_gateway.webhooks import (
    SmsReceivedPayload,
    SmsDataReceivedPayload,
    SmsBatchReceivedPayload,
    SmsBatchDataReceivedPayload,
    MmsReceivedPayload,
    MmsDownloadedPayload,
    MmsBatchReceivedPayload,
    MmsBatchDownloadedPayload,
)

# Webhook payload types: sms:received / sms:data-received


def test_sms_received_payload_from_dict():
    """
    Tests that an SmsReceivedPayload can be instantiated from a dictionary
    with all required and optional fields, and that received_at is parsed
    into a datetime instance.
    """
    payload = {
        "messageId": "msg_1",
        "phoneNumber": "+15551234567",
        "sender": "+15551234567",
        "message": "Hello from the device",
        "receivedAt": "2026-08-18T07:24:00Z",
        "recipient": "+15559876543",
        "simNumber": 2,
    }

    parsed = SmsReceivedPayload.from_dict(payload)

    assert parsed.message_id == payload["messageId"]
    assert parsed.phone_number == payload["phoneNumber"]
    assert parsed.sender == payload["sender"]
    assert parsed.message == payload["message"]
    assert parsed.received_at == datetime.datetime.fromisoformat(
        payload["receivedAt"].replace("Z", "+00:00")
    )
    assert isinstance(parsed.received_at, datetime.datetime)
    assert parsed.recipient == payload["recipient"]
    assert parsed.sim_number == payload["simNumber"]


def test_sms_received_payload_from_dict_required_fields_only():
    """
    Tests that an SmsReceivedPayload can be instantiated with only the
    required fields, leaving the optional ones as None.
    """
    payload = {
        "messageId": "msg_2",
        "phoneNumber": "+15551234567",
        "sender": "+15551234567",
        "message": "Minimal",
        "receivedAt": "2026-08-18T08:30:00+02:00",
    }

    parsed = SmsReceivedPayload.from_dict(payload)

    assert parsed.received_at == datetime.datetime.fromisoformat(payload["receivedAt"])
    assert parsed.recipient is None
    assert parsed.sim_number is None


def test_sms_data_received_payload_from_dict():
    """
    Tests that an SmsDataReceivedPayload can be instantiated from a
    dictionary with all required and optional fields, and that received_at
    is parsed into a datetime instance.
    """
    payload = {
        "messageId": "msg_3",
        "phoneNumber": "+15551112222",
        "sender": "+15551112222",
        "data": "aGVsbG8gd29ybGQ=",
        "receivedAt": "2026-08-18T09:00:00Z",
        "recipient": "+15553334444",
        "simNumber": 1,
    }

    parsed = SmsDataReceivedPayload.from_dict(payload)

    assert parsed.message_id == payload["messageId"]
    assert parsed.phone_number == payload["phoneNumber"]
    assert parsed.sender == payload["sender"]
    assert parsed.data == payload["data"]
    assert parsed.received_at == datetime.datetime.fromisoformat(
        payload["receivedAt"].replace("Z", "+00:00")
    )
    assert isinstance(parsed.received_at, datetime.datetime)
    assert parsed.recipient == payload["recipient"]
    assert parsed.sim_number == payload["simNumber"]


# Batch webhook payload types


def test_sms_batch_received_payload_from_dict():
    """
    Tests that an SmsBatchReceivedPayload parses its messages list into
    SmsReceivedPayload instances.
    """
    payload = {
        "messages": [
            {
                "messageId": "msg_1",
                "phoneNumber": "+15551234567",
                "sender": "+15551234567",
                "message": "First",
                "receivedAt": "2026-08-18T07:00:00Z",
                "simNumber": 1,
            },
            {
                "messageId": "msg_2",
                "phoneNumber": "+15557654321",
                "sender": "+15557654321",
                "message": "Second",
                "receivedAt": "2026-08-18T07:01:00Z",
                "recipient": "+15559876543",
            },
        ]
    }

    parsed = SmsBatchReceivedPayload.from_dict(payload)

    assert len(parsed.messages) == 2
    assert isinstance(parsed.messages, tuple)
    assert all(isinstance(message, SmsReceivedPayload) for message in parsed.messages)
    assert parsed.messages[0].message_id == "msg_1"
    assert parsed.messages[1].recipient == "+15559876543"
    assert isinstance(parsed.messages[0].received_at, datetime.datetime)
    assert parsed.messages[0].received_at == datetime.datetime.fromisoformat(
        payload["messages"][0]["receivedAt"].replace("Z", "+00:00")
    )
    assert parsed.messages[0].received_at.tzinfo is not None
    assert parsed.messages[1].received_at == datetime.datetime.fromisoformat(
        payload["messages"][1]["receivedAt"].replace("Z", "+00:00")
    )
    assert parsed.messages[1].received_at.tzinfo is not None
    with pytest.raises(TypeError):
        parsed.messages[0] = None


def test_sms_batch_data_received_payload_from_dict():
    """
    Tests that an SmsBatchDataReceivedPayload parses its messages list into
    SmsDataReceivedPayload instances.
    """
    payload = {
        "messages": [
            {
                "messageId": "msg_10",
                "phoneNumber": "+15551112222",
                "sender": "+15551112222",
                "data": "ZGF0YTE=",
                "receivedAt": "2026-08-18T09:00:00Z",
            },
            {
                "messageId": "msg_11",
                "phoneNumber": "+15553334444",
                "sender": "+15553334444",
                "data": "ZGF0YTI=",
                "receivedAt": "2026-08-18T09:01:00Z",
                "simNumber": 2,
            },
        ]
    }

    parsed = SmsBatchDataReceivedPayload.from_dict(payload)

    assert len(parsed.messages) == 2
    assert isinstance(parsed.messages, tuple)
    assert all(
        isinstance(message, SmsDataReceivedPayload) for message in parsed.messages
    )
    assert parsed.messages[0].data == "ZGF0YTE="
    assert parsed.messages[1].sim_number == 2
    assert parsed.messages[0].received_at == datetime.datetime.fromisoformat(
        payload["messages"][0]["receivedAt"].replace("Z", "+00:00")
    )
    assert parsed.messages[0].received_at.tzinfo is not None
    assert parsed.messages[1].received_at == datetime.datetime.fromisoformat(
        payload["messages"][1]["receivedAt"].replace("Z", "+00:00")
    )
    assert parsed.messages[1].received_at.tzinfo is not None
    with pytest.raises(TypeError):
        parsed.messages[0] = None


def test_mms_batch_received_payload_from_dict():
    """
    Tests that an MmsBatchReceivedPayload parses its messages list into
    MmsReceivedPayload instances.
    """
    payload = {
        "messages": [
            {
                "messageId": "mms_1",
                "phoneNumber": "+15551234567",
                "sender": "+15551234567",
                "transactionId": "txn_1",
                "contentClass": "personal",
                "size": 2048,
                "receivedAt": "2026-08-18T10:00:00Z",
                "subject": "Photo",
            },
            {
                "messageId": "mms_2",
                "phoneNumber": "+15557654321",
                "sender": "+15557654321",
                "transactionId": "txn_2",
                "contentClass": "advertisement",
                "size": 512,
                "receivedAt": "2026-08-18T10:05:00+03:00",
                "recipient": "+15559876543",
            },
        ]
    }

    parsed = MmsBatchReceivedPayload.from_dict(payload)

    assert len(parsed.messages) == 2
    assert isinstance(parsed.messages, tuple)
    assert all(isinstance(message, MmsReceivedPayload) for message in parsed.messages)
    assert parsed.messages[0].subject == "Photo"
    assert parsed.messages[1].recipient == "+15559876543"
    assert isinstance(parsed.messages[0].received_at, datetime.datetime)
    assert parsed.messages[0].received_at == datetime.datetime.fromisoformat(
        payload["messages"][0]["receivedAt"].replace("Z", "+00:00")
    )
    assert parsed.messages[0].received_at.tzinfo is not None
    assert parsed.messages[1].received_at == datetime.datetime.fromisoformat(
        payload["messages"][1]["receivedAt"].replace("Z", "+00:00")
    )
    assert parsed.messages[1].received_at.tzinfo is not None
    with pytest.raises(TypeError):
        parsed.messages[0] = None


def test_mms_batch_downloaded_payload_from_dict():
    """
    Tests that an MmsBatchDownloadedPayload parses its messages list into
    MmsDownloadedPayload instances.
    """
    payload = {
        "messages": [
            {
                "messageId": "mms_dl_1",
                "phoneNumber": "+15551234567",
                "sender": "+15551234567",
                "attachments": [
                    {
                        "partId": 1,
                        "contentType": "image/jpeg",
                        "name": "photo.jpg",
                        "size": 4096,
                    },
                    {
                        "partId": 2,
                        "contentType": "text/plain",
                        "data": "aGVsbG8=",
                    },
                ],
                "receivedAt": "2026-08-18T11:00:00Z",
                "body": "Full MMS body",
            },
            {
                "messageId": "mms_dl_2",
                "phoneNumber": "+15557654321",
                "sender": "+15557654321",
                "attachments": [],
                "receivedAt": "2026-08-18T11:05:00Z",
                "simNumber": 1,
            },
        ]
    }

    parsed = MmsBatchDownloadedPayload.from_dict(payload)

    assert len(parsed.messages) == 2
    assert isinstance(parsed.messages, tuple)
    assert all(isinstance(message, MmsDownloadedPayload) for message in parsed.messages)
    assert parsed.messages[0].body == "Full MMS body"
    assert len(parsed.messages[0].attachments) == 2
    assert isinstance(parsed.messages[0].attachments, list)
    assert parsed.messages[0].attachments[0].name == "photo.jpg"
    assert parsed.messages[1].attachments == []
    assert parsed.messages[1].sim_number == 1
    assert parsed.messages[0].received_at == datetime.datetime.fromisoformat(
        payload["messages"][0]["receivedAt"].replace("Z", "+00:00")
    )
    assert parsed.messages[0].received_at.tzinfo is not None
    assert parsed.messages[1].received_at == datetime.datetime.fromisoformat(
        payload["messages"][1]["receivedAt"].replace("Z", "+00:00")
    )
    assert parsed.messages[1].received_at.tzinfo is not None
    with pytest.raises(TypeError):
        parsed.messages[0] = None


@pytest.mark.parametrize(
    "payload_cls",
    [
        SmsBatchReceivedPayload,
        SmsBatchDataReceivedPayload,
        MmsBatchReceivedPayload,
        MmsBatchDownloadedPayload,
    ],
)
@pytest.mark.parametrize(
    "payload",
    [{}, {"messages": None}, {"messages": "not-a-list"}, {"messages": {}}],
)
def test_batch_payload_from_dict_missing_or_non_list_messages(payload_cls, payload):
    """
    Tests that all four batch payloads tolerate a missing or non-list
    'messages' key, resolving to an empty tuple (client-go nil-slice and
    client-php isset/is_array guard parity).
    """
    parsed = payload_cls.from_dict(payload)

    assert parsed.messages == ()
