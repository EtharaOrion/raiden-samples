def test_send_message_delivers_message(cli, sqs, tmp_path):
    import hashlib
    import json
    import uuid

    queue_name = f"send-message-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    message_body = "valid message body v7"
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
    expected_md5 = hashlib.md5(message_body.encode("utf-8")).hexdigest()
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
        assert messages[0]["Body"] == message_body
        assert messages[0]["MD5OfBody"] == expected_md5