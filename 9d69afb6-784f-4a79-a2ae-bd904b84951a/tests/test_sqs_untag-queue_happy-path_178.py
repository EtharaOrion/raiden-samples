def test_untag_queue_removes_specified_tag(cli, sqs):
    queue_name = "test-untag-queue-happy"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"keep": "yes", "remove": "no"}})

    tags_before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags_before.get("remove") == "no"
    assert tags_before.get("keep") == "yes"

    result = cli(
        "sqs", "untag-queue",
        "--queue-url", queue_url,
        "--tag-keys", "remove",
    )
    assert result.returncode == 0

    tags_after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert "remove" not in tags_after
    assert tags_after.get("keep") == "yes"