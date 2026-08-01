def test_delete_message_happy_path(cli, sqs):
    import hashlib
    import time
    import uuid

    queue_name = f"delete-message-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    body = f"message-to-delete-{uuid.uuid4().hex}"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

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
    assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
    assert message["ReceiptHandle"]

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        message["ReceiptHandle"],
    )
    assert result.returncode == 0

    attributes = {}
    for _ in range(20):
        state = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )
        attributes = state["Attributes"]
        if (
            attributes.get("ApproximateNumberOfMessages") == "0"
            and attributes.get("ApproximateNumberOfMessagesNotVisible") == "0"
        ):
            break
        time.sleep(0.1)

    assert attributes["ApproximateNumberOfMessages"] == "0"
    assert attributes["ApproximateNumberOfMessagesNotVisible"] == "0"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith(f"/{queue_name}") for url in listed.get("QueueUrls", [])
    )