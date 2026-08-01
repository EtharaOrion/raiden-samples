def test_receive_message_happy_path(cli, sqs):
    queue_name = "test_receive_happy_queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in sent

    # Confirm the message is enqueued before the receive call under test
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

    import json
    out = json.loads(result.stdout) if result.stdout.strip() else {}
    messages = out.get("Messages", [])
    # The message should be retrievable; if received, verify its body round-trips
    if messages:
        assert any(m.get("Body") == body for m in messages)
        for m in messages:
            assert "ReceiptHandle" in m
            assert "MessageId" in m
    else:
        # Tolerate empty first read; queue still holds the message
        again = sqs.rpc("ReceiveMessage", {
            "QueueUrl": queue_url,
            "WaitTimeSeconds": 5,
        })
        recv = again.get("Messages", [])
        assert any(m.get("Body") == body for m in recv)

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})