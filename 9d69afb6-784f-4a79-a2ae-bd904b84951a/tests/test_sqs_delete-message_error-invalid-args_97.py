def test_delete_message_missing_required_queue_url(cli, sqs):
    queue_name = "test-delete-msg-missing-url-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a message so the queue is non-empty (state we can verify unchanged)
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in sent

    # Invoke delete-message omitting the required --queue-url option
    result = cli("sqs", "delete-message", "--receipt-handle", "some-bogus-handle")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "queue-url" in result.stderr.lower() or "usage" in result.stderr.lower()

    # State must be unchanged: the message is still present in the queue
    attrs = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    count = int(attrs["Attributes"]["ApproximateNumberOfMessages"])
    assert count >= 1