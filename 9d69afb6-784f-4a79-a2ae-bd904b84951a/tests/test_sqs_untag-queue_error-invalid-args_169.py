def test_untag_queue_missing_queue_url_fails(cli, sqs, tmp_path):
    queue_name = "untag-missing-url-test-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(queue_name)

    # Seed a tag so we can verify it remains untouched after the failed call
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"team": "billing"}})

    # Invoke untag-queue WITHOUT the required --queue-url
    import json
    result = cli("sqs", "untag-queue", "--tag-keys", json.dumps(["team"]))

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "queue-url" in result.stderr.lower() or "usage" in result.stderr.lower()

    # State must be unchanged: the tag is still present
    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags.get("team") == "billing"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})