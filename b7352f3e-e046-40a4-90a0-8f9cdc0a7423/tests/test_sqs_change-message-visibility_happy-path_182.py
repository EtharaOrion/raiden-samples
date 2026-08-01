def test_change_message_visibility_makes_message_immediately_visible(cli, sqs):
    import hashlib
    import uuid

    queue_name = f"cmv-{uuid.uuid4().hex}"
    message_body = "change-message-visibility test message"
    expected_md5 = hashlib.md5(message_body.encode("utf-8")).hexdigest()

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "43200"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": message_body},
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    first_message = None
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
            first_message = messages[0]
            break

    assert first_message is not None
    assert first_message["Body"] == message_body
    assert first_message["MD5OfBody"] == expected_md5
    receipt_handle = first_message["ReceiptHandle"]

    result = cli(
        "sqs",
        "change-message-visibility",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        receipt_handle,
        "--visibility-timeout",
        "0",
    )
    assert result.returncode == 0

    visible_message = None
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
            visible_message = messages[0]
            break

    assert visible_message is not None
    assert visible_message["MessageId"] == sent["MessageId"]
    assert visible_message["Body"] == message_body
    assert visible_message["MD5OfBody"] == expected_md5