def test_tag_queue_adds_tags(cli, sqs, tmp_path):
    import json

    queue_name = "tag-queue-" + tmp_path.name.replace("_", "-")
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"existing": "unchanged"}})
    before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert before == {"existing": "unchanged"}

    new_tags = {"environment": "test", "owner": "cli"}
    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        queue_url,
        "--tags",
        json.dumps(new_tags),
    )

    assert result.returncode == 0
    after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert after == {
        "existing": "unchanged",
        "environment": "test",
        "owner": "cli",
    }