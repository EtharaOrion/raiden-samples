def test_tag_queue_adds_tags(cli, sqs):
    import json
    import uuid

    queue_name = f"tag-queue-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert not before.get("Tags")

    expected_tags = {
        "environment": "test",
        "cost-center": "integration",
    }
    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        queue_url,
        "--tags",
        json.dumps(expected_tags),
    )

    assert result.returncode == 0

    after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert after.get("Tags") == expected_tags