def test_purge_queue_removes_available_messages(cli, sqs):
    import time
    import uuid

    queue_name = "purge-" + uuid.uuid4().hex
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "message to purge"},
    )
    assert sent.get("MessageId")

    deadline = time.monotonic() + 65
    while True:
        before = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )
        if int(before["Attributes"]["ApproximateNumberOfMessages"]) >= 1:
            break
        assert time.monotonic() < deadline, "seeded message never became visible"
        time.sleep(0.5)

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
        assert time.monotonic() < deadline, "queue did not become empty after purge"
        time.sleep(0.5)