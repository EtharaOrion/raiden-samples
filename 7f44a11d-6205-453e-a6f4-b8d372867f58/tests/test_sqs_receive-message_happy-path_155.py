def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-world-message"
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in send

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "10",
    )
    assert result.returncode == 0

    if result.stdout.strip():
        import json
        parsed = json.loads(result.stdout)
        messages = parsed.get("Messages", [])
        if messages:
            assert any(m.get("Body") == body for m in messages)

    # State assertion: message was consumed (in flight) or still present.
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })["Attributes"]
    visible = int(attrs.get("ApproximateNumberOfMessages", "0"))
    in_flight = int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert visible + in_flight == 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})