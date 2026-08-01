def test_tag_queue_invalid_args(cli, sqs):
    queue_name = "tag-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    result = cli(
        "sqs", "tag-queue",
        "--queue-url", queue_url,
        "--tags", '{"env":"prod"}',
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ption" in result.stderr or "rror" in result.stderr or "Unknown" in result.stderr

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert "env" not in (tags.get("Tags") or {})