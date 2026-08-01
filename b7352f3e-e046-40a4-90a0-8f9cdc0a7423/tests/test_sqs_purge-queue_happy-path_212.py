def test_purge_queue_removes_available_messages(cli, sqs, tmp_path):
    import hashlib
    import time

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"purge-queue-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    for index in range(3):
        sent = sqs.rpc(
            "SendMessage",
            {
                "QueueUrl": queue_url,
                "MessageBody": f"message-{index}",
            },
        )
        assert sent.get("MessageId")

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert int(before["Attributes"]["ApproximateNumberOfMessages"]) > 0

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
        remaining = int(after["Attributes"]["ApproximateNumberOfMessages"])
        if remaining == 0 or time.monotonic() >= deadline:
            break
        time.sleep(1)

    assert remaining == 0