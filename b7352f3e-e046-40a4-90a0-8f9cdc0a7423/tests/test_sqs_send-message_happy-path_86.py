def test_send_message_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode("utf-8")).hexdigest()[:16]
    queue_name = f"send-message-{suffix}"
    message_body = f"hello from send-message test {suffix}"

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
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "0"

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
    expected_md5 = hashlib.md5(message_body.encode("utf-8")).hexdigest()
    assert output["MD5OfMessageBody"] == expected_md5

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"

    messages = []
    for _ in range(3):
        received = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 2,
            },
        )
        messages = received.get("Messages", [])
        if messages:
            break

    assert len(messages) == 1
    message = messages[0]
    assert message["MessageId"] == output["MessageId"]
    assert message["Body"] == message_body
    assert message["MD5OfBody"] == expected_md5