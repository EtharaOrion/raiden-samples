def test_purge_queue_removes_messages(cli, sqs):
    queue_name = "test-purge-queue-happy"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    for i in range(3):
        sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": f"msg-{i}"})

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    import time
    deadline = time.time() + 10
    count = None
    while time.time() < deadline:
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })
        count = int(attrs["Attributes"]["ApproximateNumberOfMessages"])
        if count == 0:
            break
        time.sleep(0.5)
    assert count == 0