def test_purge_queue_removes_available_messages(cli, sqs, tmp_path):
    import time

    safe_suffix = "".join(
        character if character in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" else "-"
        for character in tmp_path.name
    )
    queue_name = "purge-" + (safe_suffix[:60] or "queue")

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(queue_name)

    for body in ("message-one", "message-two"):
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent.get("MessageId")
        assert sent.get("MD5OfMessageBody")

    deadline = time.monotonic() + 10
    before_count = 0
    while time.monotonic() < deadline:
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )["Attributes"]
        before_count = int(attributes["ApproximateNumberOfMessages"])
        if before_count == 2:
            break
        time.sleep(0.2)
    assert before_count == 2

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    deadline = time.monotonic() + 60
    remaining_count = None
    while time.monotonic() < deadline:
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )["Attributes"]
        remaining_count = int(attributes["ApproximateNumberOfMessages"])
        if remaining_count == 0:
            break
        time.sleep(0.5)

    assert remaining_count == 0
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith(queue_name) for url in listed.get("QueueUrls", []))