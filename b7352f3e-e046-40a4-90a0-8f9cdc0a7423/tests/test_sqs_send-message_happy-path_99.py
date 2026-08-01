def test_send_message_delivers_body_and_md5(cli, sqs):
    import hashlib
    import json
    import uuid

    queue_name = "send-message-" + uuid.uuid4().hex
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert int(before["Attributes"]["ApproximateNumberOfMessages"]) == 0

    message_body = "valid SQS message: hello, Ω!"
    expected_md5 = hashlib.md5(message_body.encode("utf-8")).hexdigest()

    result = cli(
        "sqs",
        "send-message",
        "--queue-url",
        queue_url,
        "--message-body",
        message_body,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["MessageId"]
    assert output["MD5OfMessageBody"] == expected_md5

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert int(after["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    messages = []
    for _ in range(3):
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
            break

    assert messages
    assert messages[0]["MessageId"] == output["MessageId"]
    assert messages[0]["Body"] == message_body
    assert messages[0]["MD5OfBody"] == expected_md5