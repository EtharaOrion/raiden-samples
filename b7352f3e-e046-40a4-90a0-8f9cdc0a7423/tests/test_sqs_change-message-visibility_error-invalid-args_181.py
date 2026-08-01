def test_change_message_visibility_rejects_unknown_flag(cli, sqs):
    queue_name = "change-visibility-invalid-args"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "0"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message-must-remain-visible"
    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"]

    received_message = None
    for _ in range(3):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        if response.get("Messages"):
            received_message = response["Messages"][0]
            break

    assert received_message is not None
    assert received_message["Body"] == body
    assert received_message["MD5OfBody"] == sent["MD5OfMessageBody"]

    result = cli(
        "sqs",
        "change-message-visibility",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        received_message["ReceiptHandle"],
        "--visibility-timeout",
        "43200",
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    message_after_error = None
    for _ in range(3):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        if response.get("Messages"):
            message_after_error = response["Messages"][0]
            break

    assert message_after_error is not None
    assert message_after_error["Body"] == body
    assert message_after_error["MD5OfBody"] == sent["MD5OfMessageBody"]