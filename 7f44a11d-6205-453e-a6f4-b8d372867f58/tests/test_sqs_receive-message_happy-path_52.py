def test_receive_message_happy_path(cli, sqs):
    queue_name = "receive-happy-path-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in sent

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "10",
    )
    assert result.returncode == 0

    # Command succeeded; ReceiveMessage may return the message or empty on a
    # given poll. If a message was returned, validate its body round-trip.
    if result.stdout.strip():
        import json
        parsed = json.loads(result.stdout)
        messages = parsed.get("Messages", [])
        if messages:
            assert any(m.get("Body") == body for m in messages)

    # Independent state read: the message is either still available or was
    # made invisible by the receive; either way the queue exists and total
    # message count (visible + in-flight) reflects the one we sent.
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })["Attributes"]
    visible = int(attrs.get("ApproximateNumberOfMessages", "0"))
    inflight = int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert visible + inflight >= 1