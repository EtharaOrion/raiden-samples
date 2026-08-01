def test_list_queue_tags_rejects_invalid_attribute_definitions(cli, sqs, tmp_path):
    import hashlib

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"list-tags-invalid-{suffix}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": {"purpose": "invalid-args"}})

    result = cli(
        "sqs",
        "list-queue-tags",
        "--queue-url",
        queue_url,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    tags = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags == {"purpose": "invalid-args"}