def test_delete_message_removes_received_message(cli, sqs):
    import hashlib
    import time
    import uuid

    queue_name = f"delete-message-{uuid.uuid4().hex}"
    body = "message to delete"
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "60"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    message = None
    for _ in range(5):
        received = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        messages = received.get("Messages", [])
        if messages:
            message = messages[0]
            break

    assert message is not None
    assert message["Body"] == body
    assert message["MD5OfBody"] == expected_md5
    receipt_handle = message["ReceiptHandle"]

    deadline = time.monotonic() + 5
    while True:
        before = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )["Attributes"]
        if before.get("ApproximateNumberOfMessagesNotVisible") == "1":
            break
        assert time.monotonic() < deadline
        time.sleep(0.1)

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        receipt_handle,
    )
    assert result.returncode == 0

    deadline = time.monotonic() + 5
    while True:
        after = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )["Attributes"]
        if (
            after.get("ApproximateNumberOfMessages") == "0"
            and after.get("ApproximateNumberOfMessagesNotVisible") == "0"
        ):
            break
        assert time.monotonic() < deadline
        time.sleep(0.1)