def test_tag_queue_nonexistent_queue_fails_without_creating_queue(cli, sqs, tmp_path):
    import uuid

    suffix = uuid.uuid4().hex
    existing_name = f"tag-sentinel-{suffix}"
    missing_name = f"tag-missing-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": existing_name})
    existing_url = created["QueueUrl"]
    assert existing_url.endswith("/" + existing_name)

    missing_url = existing_url.rsplit("/", 1)[0] + "/" + missing_name
    before = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert before.get("QueueUrls", []) == []

    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        missing_url,
        "--tags",
        '{"purpose":"nonexistent-queue-test"}',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert after.get("QueueUrls", []) == []

    existing_after = sqs.rpc("GetQueueUrl", {"QueueName": existing_name})
    assert existing_after["QueueUrl"].endswith("/" + existing_name)