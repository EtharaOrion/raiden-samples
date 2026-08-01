def test_purge_queue_missing_required_queue_url(cli, sqs):
    queue_name = "purge-missing-arg-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    try:
        # Seed a message so we can verify the queue is untouched by the failed call.
        sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
        assert sent.get("MessageId")

        # Run the command under test WITHOUT the required --queue-url option.
        result = cli("sqs", "purge-queue")

        assert result.returncode != 0
        assert not result.stdout.strip(), result.stdout
        assert "queue-url" in result.stderr.lower() or "argument" in result.stderr.lower()

        # State: the queue still exists and still has its message (nothing purged).
        listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
        assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))

        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })["Attributes"]
        assert int(attrs["ApproximateNumberOfMessages"]) >= 1
    finally:
        sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})