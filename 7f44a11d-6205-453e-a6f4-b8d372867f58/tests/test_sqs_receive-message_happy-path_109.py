def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in sent

    # Ensure the message is enqueued before receiving
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    # Command under test: use long-poll to make receipt deterministic
    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "10",
    )
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    messages = payload.get("Messages", [])
    assert len(messages) >= 1
    msg = messages[0]
    assert msg["Body"] == body
    assert "ReceiptHandle" in msg
    assert msg["MessageId"] == sent["MessageId"]

    # Independent state check: message is now in-flight (invisible)
    attrs2 = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
    })
    assert int(attrs2["Attributes"]["ApproximateNumberOfMessagesNotVisible"]) >= 1