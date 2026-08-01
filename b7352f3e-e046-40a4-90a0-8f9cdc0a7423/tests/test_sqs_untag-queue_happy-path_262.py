def test_untag_queue_removes_specified_tags(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"untag-queue-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    sqs.rpc(
        "TagQueue",
        {
            "QueueUrl": queue_url,
            "Tags": {
                "remove-one": "first",
                "remove-two": "second",
                "keep": "retained",
            },
        },
    )
    before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert before["Tags"] == {
        "remove-one": "first",
        "remove-two": "second",
        "keep": "retained",
    }

    result = cli(
        "sqs",
        "untag-queue",
        "--queue-url",
        queue_url,
        "--tag-keys",
        json.dumps(["remove-one", "remove-two"]),
    )

    assert result.returncode == 0

    after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert after.get("Tags", {}) == {"keep": "retained"}