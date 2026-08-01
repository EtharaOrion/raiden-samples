def test_tag_queue_rejects_unknown_flag_without_changing_tags(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:12]
    queue_name = f"tag-invalid-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    original_tags = {"existing": "preserved"}
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": original_tags})

    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        queue_url,
        "--tags",
        json.dumps({"new": "value"}),
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    tags_after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags_after == original_tags