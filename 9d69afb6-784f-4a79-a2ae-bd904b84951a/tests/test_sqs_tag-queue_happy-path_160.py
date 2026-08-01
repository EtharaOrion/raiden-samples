def test_tag_queue_adds_tag(cli, sqs):
    queue_name = "test-tag-queue-happy"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    import json
    result = cli(
        "sqs", "tag-queue",
        "--queue-url", queue_url,
        "--tags", json.dumps({"Environment": "production", "Team": "backend"}),
    )
    assert result.returncode == 0

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags.get("Environment") == "production"
    assert tags.get("Team") == "backend"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})