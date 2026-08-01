def test_send_message_happy_path(cli, sqs):
    queue_name = "test-send-happy-path-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello world happy path body"
    result = cli(
        "sqs", "send-message",
        "--queue-url", queue_url,
        "--message-body", body,
        "--delay-seconds", "0",
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    assert "MessageId" in out and out["MessageId"]
    assert "MD5OfMessageBody" in out

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})