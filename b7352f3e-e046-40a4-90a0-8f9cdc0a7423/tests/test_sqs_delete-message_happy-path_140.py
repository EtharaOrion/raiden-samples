def test_delete_message_happy_path(cli, sqs):
    import hashlib
    import time
    import uuid

    queue_name = f"delete-message-{uuid.uuid4().hex}"
    queue = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "5"},
        },
    )
    queue_url = queue["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    body = "message to delete"
    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    received_at = time.monotonic()
    received = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 2,
        },
    )
    messages = received.get("Messages", [])
    assert len(messages) == 1
    assert messages[0]["Body"] == body
    assert messages[0]["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
    receipt_handle = messages[0]["ReceiptHandle"]

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        receipt_handle,
    )
    assert result.returncode == 0

    remaining_visibility = 5.2 - (time.monotonic() - received_at)
    if remaining_visibility > 0:
        time.sleep(remaining_visibility)

    after = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 2,
        },
    )
    assert not after.get("Messages")