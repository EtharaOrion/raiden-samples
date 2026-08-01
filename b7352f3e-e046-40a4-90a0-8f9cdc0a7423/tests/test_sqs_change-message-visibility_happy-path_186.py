def test_change_message_visibility_makes_message_immediately_visible(cli, sqs, tmp_path):
    queue_name = "change-visibility-" + str(abs(hash(str(tmp_path))))
    body = "message-" + str(abs(hash(queue_name)))

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "300"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

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
    assert received_message["MD5OfBody"] == sent["MD5OfMessageBody"]
    assert received_message["ReceiptHandle"]

    while_invisible = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 0,
        },
    )
    assert not while_invisible.get("Messages")

    result = cli(
        "sqs",
        "change-message-visibility",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        received_message["ReceiptHandle"],
        "--visibility-timeout",
        "0",
    )
    assert result.returncode == 0

    visible_again = None
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
            visible_again = messages[0]
            break

    assert visible_again is not None
    assert visible_again["MessageId"] == sent["MessageId"]
    assert visible_again["Body"] == body
    assert visible_again["MD5OfBody"] == sent["MD5OfMessageBody"]