def test_purge_queue_removes_messages(cli, sqs):
    queue_name = "test-purge-happy-path-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed messages
    for i in range(3):
        sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": f"msg-{i}"})
        assert "MessageId" in sent

    # Confirm messages present before purge
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    # Run command under test
    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    # Assert resulting state: eventually 0 messages
    count = None
    for _ in range(20):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })
        count = int(attrs["Attributes"]["ApproximateNumberOfMessages"])
        if count == 0:
            break
    assert count == 0