def test_untag_queue_removes_specified_tag(cli, sqs, tmp_path):
    queue_name = "untag-" + tmp_path.name[-40:].replace("_", "-")
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

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
    before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert before["Tags"] == {
        "remove-me": "obsolete",
        "keep-me": "retained",
    }

    result = cli(
        "sqs",
        "untag-queue",
        "--queue-url",
        queue_url,
        "--tag-keys",
        '["remove-me"]',
    )

    assert result.returncode == 0
    after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert after.get("Tags", {}) == {"keep-me": "retained"}