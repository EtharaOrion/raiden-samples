def test_purge_queue_removes_messages(cli, sqs, tmp_path):
    import json, time

    queue_name = "purge-happy-test-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith(queue_name)

    # Seed messages
    for i in range(3):
        sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": f"msg-{i}"})
        assert "MessageId" in sent

    # Confirm messages present before purge (tolerate eventual consistency)
    present = False
    for _ in range(10):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })["Attributes"]
        if int(attrs.get("ApproximateNumberOfMessages", "0")) > 0:
            present = True
            break
        time.sleep(0.2)
    assert present

    # Command under test
    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    # After purge, message count should reach 0 (tolerating eventual consistency)
    purged = False
    for _ in range(15):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })["Attributes"]
        if int(attrs.get("ApproximateNumberOfMessages", "0")) == 0:
            purged = True
            break
        time.sleep(0.3)
    assert purged