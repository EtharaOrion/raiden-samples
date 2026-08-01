def test_untag_queue_removes_requested_tags(cli, sqs, tmp_path):
    import uuid

    queue_name = f"untag-{uuid.uuid4().hex}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]

    sqs.rpc(
        "TagQueue",
        {
            "QueueUrl": queue_url,
            "Tags": {
                "remove-me": "obsolete",
                "keep-me": "retained",
            },
        },
    )
    initial_tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert initial_tags["remove-me"] == "obsolete"
    assert initial_tags["keep-me"] == "retained"

    result = cli(
        "sqs",
        "untag-queue",
        "--queue-url",
        queue_url,
        "--tag-keys",
        '["remove-me"]',
    )

    assert result.returncode == 0
    resulting_tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert "remove-me" not in resulting_tags
    assert resulting_tags["keep-me"] == "retained"