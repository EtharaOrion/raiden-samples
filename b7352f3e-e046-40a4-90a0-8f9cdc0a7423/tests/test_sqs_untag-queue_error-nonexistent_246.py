def test_untag_queue_nonexistent(cli, sqs, tmp_path):
    import uuid

    suffix = uuid.uuid4().hex
    sentinel_name = f"untag-sentinel-{suffix}"
    missing_name = f"untag-missing-{suffix}"

    sentinel_url = sqs.rpc(
        "CreateQueue",
        {"QueueName": sentinel_name},
    )["QueueUrl"]
    sqs.rpc(
        "TagQueue",
        {
            "QueueUrl": sentinel_url,
            "Tags": {"remove-me": "preserve", "other": "value"},
        },
    )

    missing_url = sentinel_url.rsplit("/", 1)[0] + "/" + missing_name
    before = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert not any(
        url.endswith("/" + missing_name) for url in before.get("QueueUrls", [])
    )

    result = cli(
        "sqs",
        "untag-queue",
        "--queue-url",
        missing_url,
        "--tag-keys",
        '["remove-me"]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert not any(
        url.endswith("/" + missing_name) for url in after.get("QueueUrls", [])
    )
    tags = sqs.rpc("ListQueueTags", {"QueueUrl": sentinel_url}).get("Tags", {})
    assert tags == {"remove-me": "preserve", "other": "value"}