def test_send_message_delivers_message(cli, sqs, tmp_path):
    import hashlib
    import json

    queue_name = "send-message-" + hashlib.sha256(
        str(tmp_path).encode("utf-8")
    ).hexdigest()[:20]
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    message_body = "valid send-message payload v3"
    expected_md5 = hashlib.md5(message_body.encode("utf-8")).hexdigest()

    result = cli(
        "sqs",
        "send-message",
        "--queue-url",
        queue_url,
        "--message-body",
        message_body,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["MessageId"]
    assert output["MD5OfMessageBody"] == expected_md5

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert int(attributes["Attributes"]["ApproximateNumberOfMessages"]) == 1

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

    assert len(messages) == 1
    assert messages[0]["Body"] == message_body
    assert messages[0]["MD5OfBody"] == expected_md5