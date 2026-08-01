def test_tag_queue_adds_tag(cli, sqs):
    queue_name = "test-tag-queue-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs", "tag-queue",
        "--queue-url", queue_url,
        "--tags", '{"env":"prod","team":"data"}',
    )
    assert result.returncode == 0

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags.get("env") == "prod"
    assert tags.get("team") == "data"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})