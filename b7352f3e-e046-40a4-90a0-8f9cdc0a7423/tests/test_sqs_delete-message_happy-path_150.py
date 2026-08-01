def test_delete_message_removes_received_message(cli, sqs):
    import hashlib
    import time
    import uuid

    queue_name = f"delete-message-{uuid.uuid4().hex}"
    queue_url = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    body = "message to delete"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
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
    assert message["MessageId"] == sent["MessageId"]
    assert message["ReceiptHandle"]

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
        },
    )["Attributes"]
    assert int(before["ApproximateNumberOfMessagesNotVisible"]) == 1

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        message["ReceiptHandle"],
    )
    assert result.returncode == 0

    remaining = None
    for _ in range(20):
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )["Attributes"]
        remaining = (
            int(attributes["ApproximateNumberOfMessages"])
            + int(attributes["ApproximateNumberOfMessagesNotVisible"])
        )
        if remaining == 0:
            break
        time.sleep(0.25)

    assert remaining == 0