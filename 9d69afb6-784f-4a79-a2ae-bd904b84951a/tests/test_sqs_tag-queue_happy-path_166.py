def test_tag_queue_adds_tag(cli, sqs):
    queue_name = "tag-queue-happy-test"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]

    result = cli(
        "sqs", "tag-queue",
        "--queue-url", queue_url,
        "--tags", '{"env":"prod","team":"payments"}',
    )
    assert result.returncode == 0

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags.get("env") == "prod"
    assert tags.get("team") == "payments"