def test_change_message_visibility_makes_message_immediately_visible(cli, sqs, tmp_path):
    queue_name = "cmv-" + str(abs(hash(str(tmp_path))))
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "120"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "change-message-visibility round trip"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"]

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
    assert first_message["Body"] == body
    assert first_message["MD5OfBody"] == sent["MD5OfMessageBody"]
    assert first_message["ReceiptHandle"]

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

    visible_message = None
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
            visible_message = messages[0]
            break

    assert visible_message is not None
    assert visible_message["MessageId"] == sent["MessageId"]
    assert visible_message["Body"] == body
    assert visible_message["MD5OfBody"] == sent["MD5OfMessageBody"]