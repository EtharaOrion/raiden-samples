def test_untag_queue_removes_tag(cli, sqs):
    queue_name = "untag-happy-test-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"env": "prod", "team": "core"}})

    before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert before.get("env") == "prod"
    assert before.get("team") == "core"

    result = cli(
        "sqs", "untag-queue",
        "--queue-url", queue_url,
        "--tag-keys", "env",
    )
    assert result.returncode == 0

    after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert "env" not in after
    assert after.get("team") == "core"