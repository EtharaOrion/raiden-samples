def test_purge_queue_removes_available_messages(cli, sqs, tmp_path):
    import time
    import uuid

    queue_name = f"purge-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    for body in ("message-one", "message-two"):
        sent = sqs.rpc(
            "SendMessage",
            {
                "QueueUrl": queue_url,
                "MessageBody": body,
            },
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"]

    deadline = time.monotonic() + 65
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
        if before_count >= 2:
            break
        time.sleep(1)
    assert before_count >= 2

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    deadline = time.monotonic() + 65
    after_count = None
    while time.monotonic() < deadline:
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )["Attributes"]
        after_count = int(attributes["ApproximateNumberOfMessages"])
        if after_count == 0:
            break
        time.sleep(1)

    assert after_count == 0