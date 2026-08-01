def test_delete_message_removes_received_message(cli, sqs, tmp_path):
    import hashlib
    import time

    queue_name = ("delete-message-" + tmp_path.name)[:80]
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "0"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message to delete"
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    for _ in range(20):
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )["Attributes"]
        if int(attributes["ApproximateNumberOfMessages"]) >= 1:
            break
        time.sleep(0.1)
    assert int(attributes["ApproximateNumberOfMessages"]) >= 1

    message = None
    for _ in range(10):
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

    for _ in range(30):
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
            break
        time.sleep(0.1)

    assert attributes["ApproximateNumberOfMessages"] == "0"
    assert attributes["ApproximateNumberOfMessagesNotVisible"] == "0"