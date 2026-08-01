def test_untag_queue_invalid_flag_rejected(cli, sqs):
    qname = "untag-invalid-flag-queue"
    created = sqs.rpc("CreateQueue", {
        "QueueName": qname,
        "Attributes": {},
    })
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    # Seed a tag so we can verify it survives the failed call
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"env": "prod"}})

    result = cli(
        "sqs", "untag-queue",
        "--queue-url", queue_url,
        "--tag-keys", "env",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    # State must be unchanged: the tag should still be present
    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags.get("env") == "prod"