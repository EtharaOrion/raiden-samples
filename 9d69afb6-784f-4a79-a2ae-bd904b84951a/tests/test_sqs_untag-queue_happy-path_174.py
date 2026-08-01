def test_untag_queue_removes_tag(cli, sqs, tmp_path):
    queue_name = "untag-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

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