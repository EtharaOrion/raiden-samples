def test_purge_queue_removes_available_messages(cli, sqs):
    import time
    import uuid

    queue_name = "purge-test-" + uuid.uuid4().hex
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    for body in ("message-one", "message-two"):
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent.get("MessageId")
        assert sent.get("MD5OfMessageBody")

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert int(before["Attributes"]["ApproximateNumberOfMessages"]) == 2

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    remaining = None
    for _ in range(20):
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )
        remaining = int(
            attributes["Attributes"]["ApproximateNumberOfMessages"]
        )
        if remaining == 0:
            break
        time.sleep(0.25)

    assert remaining == 0