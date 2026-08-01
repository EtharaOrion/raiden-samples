def test_tag_queue_adds_and_overwrites_tags(cli, sqs, tmp_path):
    import json
    import uuid

    queue_name = f"tag-queue-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc(
        "TagQueue",
        {
            "QueueUrl": queue_url,
            "Tags": {
                "environment": "old-value",
                "preserved": "existing-value",
            },
        },
    )
    before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert before == {
        "environment": "old-value",
        "preserved": "existing-value",
    }

    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        queue_url,
        "--tags",
        json.dumps(
            {
                "environment": "test",
                "owner": "candidate-cli",
            }
        ),
    )

    assert result.returncode == 0, result.stderr

    after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert after == {
        "environment": "test",
        "owner": "candidate-cli",
        "preserved": "existing-value",
    }