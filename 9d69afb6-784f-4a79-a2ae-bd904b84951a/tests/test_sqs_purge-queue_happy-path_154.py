def test_purge_queue_removes_messages(cli, sqs):
    queue_name = "purge-happy-v4"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    for i in range(3):
        sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": f"msg-{i}"})
        assert "MessageId" in sent

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    import time
    deadline = time.time() + 15
    count = None
    while time.time() < deadline:
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })["Attributes"]
        count = attrs.get("ApproximateNumberOfMessages")
        if count == "0":
            break
        time.sleep(1)
    assert count == "0"