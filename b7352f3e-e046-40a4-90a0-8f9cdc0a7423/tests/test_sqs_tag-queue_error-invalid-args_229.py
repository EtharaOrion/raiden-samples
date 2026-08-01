def test_tag_queue_missing_required_queue_url(cli, sqs, tmp_path):
    queue_name = ("tag-queue-invalid-" + tmp_path.name)[:80]
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    original_tags = {"existing": "unchanged"}
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": original_tags})

    result = cli(
        "sqs",
        "tag-queue",
        "--tags",
        '{"attempted":"value"}',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == original_tags