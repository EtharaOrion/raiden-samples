def test_purge_queue_removes_available_messages(cli, sqs, tmp_path):
    import hashlib
    import time

    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-40:]
    queue_name = f"purge-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message to be purged"
    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": body},
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    deadline = time.monotonic() + 10
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
        assert time.monotonic() < deadline
        time.sleep(0.1)

    result = cli("sqs", "purge-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    deadline = time.monotonic() + 10
    while True:
        after = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )
        attributes = after["Attributes"]
        if (
            int(attributes["ApproximateNumberOfMessages"]) == 0
            and int(attributes["ApproximateNumberOfMessagesNotVisible"]) == 0
        ):
            break
        assert time.monotonic() < deadline
        time.sleep(0.1)

    looked_up = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert looked_up["QueueUrl"].endswith("/" + queue_name)