def test_tag_queue_rejects_invalid_arguments(cli, sqs, tmp_path):
    queue_name = f"tag-invalid-{abs(hash(str(tmp_path)))}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    original_tags = {"environment": "untouched"}
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": original_tags})

    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        "x" * 512,
        "--tags",
        "<json>",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Error parsing parameter" in result.stderr

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == original_tags