def test_purge_queue_removes_available_messages(cli, sqs, tmp_path):
    import hashlib
    import time

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:20]
    queue_name = f"purge-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    for body in ("message-one", "message-two"):
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent.get("MessageId")

    deadline = time.monotonic() + 60
    while True:
        before = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )
        if int(before["Attributes"]["ApproximateNumberOfMessages"]) == 2:
            break
        if time.monotonic() >= deadline:
            assert int(before["Attributes"]["ApproximateNumberOfMessages"]) == 2
        time.sleep(0.25)

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    deadline = time.monotonic() + 60
    while True:
        after = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )
        if int(after["Attributes"]["ApproximateNumberOfMessages"]) == 0:
            break
        if time.monotonic() >= deadline:
            assert int(after["Attributes"]["ApproximateNumberOfMessages"]) == 0
        time.sleep(0.25)