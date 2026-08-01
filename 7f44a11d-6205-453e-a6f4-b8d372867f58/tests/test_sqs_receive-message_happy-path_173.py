def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert send.get("MessageId")

    # Wait for the message to be countable in the queue
    for _ in range(10):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })
        if int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1:
            break

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "10",
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    messages = out.get("Messages", [])
    assert len(messages) >= 1
    assert any(m.get("Body") == body for m in messages)

    # Independent read-back: the received message should now be invisible,
    # so the queue reports zero visible messages after the receive.
    attrs_after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
    })
    assert int(attrs_after["Attributes"]["ApproximateNumberOfMessagesNotVisible"]) >= 1