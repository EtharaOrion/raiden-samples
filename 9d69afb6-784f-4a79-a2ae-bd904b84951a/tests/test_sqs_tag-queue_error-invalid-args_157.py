def test_tag_queue_missing_queue_url(cli, sqs):
    queue_name = "test-tag-queue-missing-url"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    result = cli("sqs", "tag-queue", "--tags", '{"env":"prod"}')

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "queue-url" in result.stderr.lower() or "argument" in result.stderr.lower()

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert "env" not in (tags.get("Tags") or {})