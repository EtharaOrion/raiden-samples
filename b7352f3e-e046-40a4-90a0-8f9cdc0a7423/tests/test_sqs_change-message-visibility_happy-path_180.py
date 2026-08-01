def test_change_message_visibility_makes_message_immediately_visible(cli, sqs):
    import hashlib
    import uuid

    queue_name = f"visibility-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "43200"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "change-message-visibility round trip"
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MD5OfMessageBody"] == expected_md5

    first_message = None
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
            first_message = messages[0]
            break

    assert first_message is not None
    assert first_message["MessageId"] == sent["MessageId"]
    assert first_message["Body"] == body
    assert first_message["MD5OfBody"] == expected_md5

    result = cli(
        "sqs",
        "change-message-visibility",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        first_message["ReceiptHandle"],
        "--visibility-timeout",
        "0",
    )
    assert result.returncode == 0

    visible_again = None
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
            visible_again = messages[0]
            break

    assert visible_again is not None
    assert visible_again["MessageId"] == sent["MessageId"]
    assert visible_again["Body"] == body
    assert visible_again["MD5OfBody"] == expected_md5