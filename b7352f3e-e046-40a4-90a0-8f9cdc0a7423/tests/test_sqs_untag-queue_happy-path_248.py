def test_untag_queue_removes_selected_tags(cli, sqs, tmp_path):
    queue_name = f"untag-queue-{tmp_path.name}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc(
        "TagQueue",
        {
            "QueueUrl": queue_url,
            "Tags": {
                "remove-me": "old-value",
                "keep-me": "retained-value",
            },
        },
    )

    result = cli(
        "sqs",
        "untag-queue",
        "--queue-url",
        queue_url,
        "--tag-keys",
        '["remove-me"]',
    )

    assert result.returncode == 0
    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert "remove-me" not in tags
    assert tags.get("keep-me") == "retained-value"