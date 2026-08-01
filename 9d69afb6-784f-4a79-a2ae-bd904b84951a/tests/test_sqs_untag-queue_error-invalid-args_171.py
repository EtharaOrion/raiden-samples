def test_untag_queue_missing_tag_keys_arg(cli, sqs, tmp_path):
    queue_name = "untag-missing-tagkeys-test-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a tag so we can verify it survives the failed call.
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"env": "prod"}})

    # Invoke untag-queue WITHOUT the required --tag-keys option.
    result = cli("sqs", "untag-queue", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "tag-keys" in result.stderr.lower() or "argument" in result.stderr.lower()

    # State must be unchanged: the tag is still present.
    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags.get("env") == "prod"