def test_untag_queue_removes_tag(cli, sqs):
    queue_name = "test-untag-queue-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    sqs.rpc("TagQueue", {
        "QueueUrl": queue_url,
        "Tags": {"env": "prod", "team": "core"},
    })

    before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert before.get("Tags", {}).get("env") == "prod"
    assert before.get("Tags", {}).get("team") == "core"

    result = cli(
        "sqs", "untag-queue",
        "--queue-url", queue_url,
        "--tag-keys", "env",
    )
    assert result.returncode == 0

    after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    tags = after.get("Tags", {})
    assert "env" not in tags
    assert tags.get("team") == "core"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})