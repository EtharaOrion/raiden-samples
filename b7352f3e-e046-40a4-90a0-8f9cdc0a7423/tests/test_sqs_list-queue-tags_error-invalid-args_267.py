def test_list_queue_tags_rejects_unknown_flag(cli, sqs, tmp_path):
    queue_name = "list-tags-invalid-" + str(abs(hash(str(tmp_path))))
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"environment": "test"}})

    result = cli(
        "sqs",
        "list-queue-tags",
        "--queue-url",
        queue_url,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "unknown options" in result.stderr.lower()

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == {"environment": "test"}
    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith("/" + queue_name) for url in queues)