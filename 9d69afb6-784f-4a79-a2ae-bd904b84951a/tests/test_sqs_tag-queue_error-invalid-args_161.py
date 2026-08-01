def test_tag_queue_invalid_args(cli, sqs):
    qname = "test-tag-queue-invalid-args"
    created = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = created["QueueUrl"]

    result = cli(
        "sqs", "tag-queue",
        "--queue-url", queue_url,
        "--tags", '{"env":"prod"}',
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert tags.get("Tags", {}) == {} or "env" not in tags.get("Tags", {})