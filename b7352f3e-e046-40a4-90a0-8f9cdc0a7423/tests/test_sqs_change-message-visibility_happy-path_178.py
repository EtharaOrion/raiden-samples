def test_change_message_visibility_makes_message_immediately_visible(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )
    queue_name = ("change-visibility-" + suffix)[-80:]

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "300"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message whose visibility will be changed"
    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )

    received = None
    for _ in range(10):
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
            received = messages[0]
            break

    assert received is not None
    assert received["MessageId"] == sent["MessageId"]
    assert received["Body"] == body
    assert received["MD5OfBody"] == sent["MD5OfMessageBody"]

    result = cli(
        "sqs",
        "change-message-visibility",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        received["ReceiptHandle"],
        "--visibility-timeout",
        "0",
    )
    assert result.returncode == 0

    visible_again = None
    for _ in range(10):
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