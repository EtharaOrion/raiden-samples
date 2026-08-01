def test_untag_queue_removes_specified_tag(cli, sqs, tmp_path):
    import json
    import uuid

    queue_name = f"untag-queue-{uuid.uuid4().hex}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
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
    initial_tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert initial_tags == {
        "remove-me": "old-value",
        "keep-me": "retained-value",
    }

    result = cli(
        "sqs",
        "untag-queue",
        "--queue-url",
        queue_url,
        "--tag-keys",
        json.dumps(["remove-me"]),
    )

    assert result.returncode == 0
    resulting_tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert "remove-me" not in resulting_tags
    assert resulting_tags.get("keep-me") == "retained-value"