def test_send_message_delivers_message(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:12]
    queue_name = f"send-message-{suffix}"
    body = "Valid SQS message with Unicode: café ☕"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

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
        body,
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    assert response["MessageId"]
    assert response["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"