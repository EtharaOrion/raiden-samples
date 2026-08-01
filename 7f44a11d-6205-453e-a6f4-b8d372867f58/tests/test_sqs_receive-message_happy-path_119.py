def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    sent_message_id = sent["MessageId"]

    # Confirm message enqueued deterministically
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) == 1

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--max-number-of-messages", "1",
        "--visibility-timeout", "30",
        "--wait-time-seconds", "5",
    )
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    messages = payload.get("Messages", [])
    assert len(messages) == 1
    msg = messages[0]
    assert msg["Body"] == body
    assert msg["MessageId"] == sent_message_id
    assert "ReceiptHandle" in msg

    # State assertion: message is now in-flight (invisible), not visible
    attrs_after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
    })
    assert int(attrs_after["Attributes"]["ApproximateNumberOfMessagesNotVisible"]) == 1