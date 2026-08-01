def test_untag_queue_removes_selected_tags(cli, sqs, tmp_path):
    queue_name = "untag-" + "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-60:]

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
    initial_tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})["Tags"]
    assert initial_tags["remove-me"] == "old-value"
    assert initial_tags["keep-me"] == "retained-value"

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
    assert resulting_tags["keep-me"] == "retained-value"