def test_send_message_happy_path(cli, sqs):
    queue_name = "test-send-message-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "Hello, this is a valid message body."
    result = cli(
        "sqs", "send-message",
        "--queue-url", queue_url,
        "--message-body", body,
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    assert "MessageId" in out
    assert out.get("MessageId")

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) == 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})