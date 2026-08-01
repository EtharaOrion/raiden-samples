def test_tag_queue_adds_and_updates_tags(cli, sqs):
    import json
    import uuid

    queue_name = f"tag-queue-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    sqs.rpc(
        "TagQueue",
        {
            "QueueUrl": queue_url,
            "Tags": {
                "existing": "old-value",
                "preserved": "unchanged",
            },
        },
    )

    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        queue_url,
        "--tags",
        json.dumps(
            {
                "existing": "new-value",
                "environment": "test",
            }
        ),
    )

    assert result.returncode == 0

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == {
        "existing": "new-value",
        "preserved": "unchanged",
        "environment": "test",
    }