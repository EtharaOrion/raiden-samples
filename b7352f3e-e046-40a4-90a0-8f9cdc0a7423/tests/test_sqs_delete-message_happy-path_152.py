def test_delete_message_happy_path(cli, sqs, tmp_path):
    import hashlib

    queue_name = "delete-message-" + hashlib.sha256(
        str(tmp_path).encode("utf-8")
    ).hexdigest()[:16]
    queue = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )
    queue_url = queue["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message to delete"
    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode("utf-8")).hexdigest()

    received_message = None
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
            received_message = messages[0]
            break

    assert received_message is not None
    assert received_message["Body"] == body
    assert received_message["MD5OfBody"] == hashlib.md5(
        body.encode("utf-8")
    ).hexdigest()
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
    )["Attributes"]
    assert int(before["ApproximateNumberOfMessagesNotVisible"]) == 1

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        receipt_handle,
    )
    assert result.returncode == 0

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
    assert int(after["ApproximateNumberOfMessages"]) == 0
    assert int(after["ApproximateNumberOfMessagesNotVisible"]) == 0