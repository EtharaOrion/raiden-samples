def test_untag_queue_removes_requested_tag(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:20]
    queue_name = f"untag-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc(
        "TagQueue",
        {
            "QueueUrl": queue_url,
            "Tags": {
                "remove-me": "old-value",
                "keep-me": "preserved-value",
            },
        },
    )

    result = cli(
        "sqs",
        "untag-queue",
        "--queue-url",
        queue_url,
        "--tag-keys",
        json.dumps(["remove-me"]),
    )

    assert result.returncode == 0

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert "remove-me" not in tags
    assert tags.get("keep-me") == "preserved-value"