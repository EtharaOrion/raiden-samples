def test_purge_queue_removes_available_messages(cli, sqs, tmp_path):
    import time
    import uuid

    queue_name = f"purge-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    for index in range(3):
        sent = sqs.rpc(
            "SendMessage",
            {
                "QueueUrl": queue_url,
                "MessageBody": f"message-to-purge-{index}",
            },
        )
        assert sent.get("MessageId")
        assert sent.get("MD5OfMessageBody")

    deadline = time.monotonic() + 65
    while True:
        before = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )
        if int(before["Attributes"]["ApproximateNumberOfMessages"]) >= 3:
            break
        assert time.monotonic() < deadline
        time.sleep(1)

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    deadline = time.monotonic() + 65
    while True:
        after = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )
        if after["Attributes"]["ApproximateNumberOfMessages"] == "0":
            break
        assert time.monotonic() < deadline
        time.sleep(1)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))