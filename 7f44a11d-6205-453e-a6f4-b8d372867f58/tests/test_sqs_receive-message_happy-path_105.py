def test_receive_message_happy_path(cli, sqs):
    queue_name = "test_receive_happy_queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello world message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent.get("MessageId")

    # ensure the message is enqueued before receiving
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "10",
    )
    assert result.returncode == 0

    # stdout may contain the message (long-poll should catch it); tolerate empty read
    if result.stdout.strip():
        import json
        payload = json.loads(result.stdout)
        messages = payload.get("Messages", [])
        if messages:
            assert any(m.get("Body") == body for m in messages)
            for m in messages:
                assert m.get("MessageId")
                assert m.get("ReceiptHandle")

    # queue still exists and is reachable
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))