def test_untag_queue_missing_required_tag_keys(cli, sqs):
    import uuid

    queue_name = f"untag-missing-keys-{uuid.uuid4().hex}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"environment": "test"}})

    result = cli("sqs", "untag-queue", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--tag-keys" in result.stderr

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags.get("environment") == "test"