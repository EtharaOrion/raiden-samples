def test_purge_queue_nonexistent(cli, sqs, tmp_path):
    import uuid

    suffix = uuid.uuid4().hex
    existing_name = f"purge-sentinel-{suffix}"
    missing_name = f"purge-missing-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": existing_name})
    existing_url = created["QueueUrl"]
    sqs.rpc(
        "SendMessage",
        {"QueueUrl": existing_url, "MessageBody": "must-not-be-purged"},
    )

    missing_url = existing_url.rsplit("/", 1)[0] + "/" + missing_name
    result = cli("sqs", "purge-queue", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": existing_name})
    assert any(
        url.endswith("/" + existing_name) for url in queues.get("QueueUrls", [])
    )

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": existing_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert attributes["Attributes"]["ApproximateNumberOfMessages"] == "1"