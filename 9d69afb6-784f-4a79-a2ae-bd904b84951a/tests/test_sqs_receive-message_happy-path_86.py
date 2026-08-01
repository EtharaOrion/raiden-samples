def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in sent

    # Confirm message is in the queue before receiving
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    # Run the command under test; tolerate empty first read (short poll)
    received_body = None
    for _ in range(10):
        result = cli(
            "sqs", "receive-message",
            "--queue-url", queue_url,
            "--wait-time-seconds", "1",
        )
        assert result.returncode == 0, result.stderr
        out = result.stdout.strip()
        if out:
            import json
            parsed = json.loads(out)
            msgs = parsed.get("Messages", [])
            if msgs:
                received_body = msgs[0]["Body"]
                break

    assert received_body == body