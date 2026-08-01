def test_delete_message_removes_received_message(cli, sqs):
    import hashlib
    import time
    import uuid

    queue_name = f"delete-message-{uuid.uuid4().hex}"
    queue = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "0"},
        },
    )
    queue_url = queue["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message to delete"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    received_message = None
    for _ in range(5):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        messages = response.get("Messages", [])
        if messages:
            received_message = messages[0]
            break

    assert received_message is not None
    assert received_message["Body"] == body
    assert received_message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
    receipt_handle = received_message["ReceiptHandle"]

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": [
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
            ],
        },
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        receipt_handle,
    )
    assert result.returncode == 0

    remaining = None
    for _ in range(10):
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
        if (
            attributes["ApproximateNumberOfMessages"] == "0"
            and attributes["ApproximateNumberOfMessagesNotVisible"] == "0"
        ):
            remaining = attributes
            break
        time.sleep(0.2)

    assert remaining is not None