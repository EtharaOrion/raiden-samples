def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-path-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in sent

    # Wait until the message is available before the receive-message call
    for _ in range(20):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })
        if int(attrs["Attributes"].get("ApproximateNumberOfMessages", "0")) >= 1:
            break

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--max-number-of-messages", "1",
        "--visibility-timeout", "30",
        "--wait-time-seconds", "5",
    )
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    messages = out.get("Messages", [])
    assert len(messages) >= 1
    msg = messages[0]
    assert msg["Body"] == body
    assert msg["MessageId"] == sent["MessageId"]
    assert "ReceiptHandle" in msg

    # After receipt with a 30s visibility timeout the message must be invisible.
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
    })
    assert int(attrs["Attributes"].get("ApproximateNumberOfMessagesNotVisible", "0")) >= 1