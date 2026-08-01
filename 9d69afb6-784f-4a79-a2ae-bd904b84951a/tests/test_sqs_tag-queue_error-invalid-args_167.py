def test_tag_queue_invalid_args_missing_tags(cli, sqs, tmp_path):
    queue_name = "tag-queue-invalid-args-test"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    # Invoke with a duplicated --queue-url but no --tags at all: invalid args.
    result = cli(
        "sqs", "tag-queue",
        "--queue-url", queue_url,
        "--queue-url", queue_url,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "argument" in result.stderr.lower() or "usage" in result.stderr.lower()

    # State assertion: no tags were added to the queue.
    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert not tags.get("Tags")