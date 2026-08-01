def test_send_message_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json

    queue_name = "send-message-" + hashlib.sha256(
        str(tmp_path).encode("utf-8")
    ).hexdigest()[:16]
    message_body = "valid message body v5"

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
    assert output["MD5OfMessageBody"] == hashlib.md5(
        message_body.encode("utf-8")
    ).hexdigest()

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"