def test_tag_queue_rejects_unknown_attribute_definitions_without_modifying_tags(cli, sqs):
    import json
    import uuid

    queue_name = f"tag-queue-invalid-args-{uuid.uuid4().hex}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    original_tags = {"existing": "preserved"}
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": original_tags})

    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        queue_url,
        "--tags",
        json.dumps({"attempted": "not-added"}),
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    tags_after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url}).get("Tags", {})
    assert tags_after == original_tags