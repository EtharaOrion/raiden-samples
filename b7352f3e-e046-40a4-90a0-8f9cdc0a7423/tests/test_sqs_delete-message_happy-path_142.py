def test_delete_message_happy_path(cli, sqs, tmp_path):
    import time

    suffix = "".join(
        char if char.isalnum() or char in "-_" else "-"
        for char in tmp_path.name
    )
    queue_name = ("delete-message-" + suffix)[:80]
    queue_url = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "1"},
        },
    )["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message to delete"
    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": body},
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"]

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
    assert message["MD5OfBody"] == sent["MD5OfMessageBody"]
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

    time.sleep(2)
    for _ in range(3):
        after = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        assert not after.get("Messages")