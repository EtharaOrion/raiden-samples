def test_tag_queue_adds_tags(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"tag-queue-{suffix}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    expected_tags = {
        "environment": "test",
        "owner": "pytest",
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
    observed = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert observed.get("Tags") == expected_tags