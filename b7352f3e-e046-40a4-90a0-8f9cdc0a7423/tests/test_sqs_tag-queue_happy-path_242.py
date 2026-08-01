def test_tag_queue_adds_tags(cli, sqs, tmp_path):
    import json

    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-50:]
    queue_name = f"tag-queue-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    before = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert not before.get("Tags")

    expected_tags = {
        "environment": "test",
        "owner": "black-box",
    }
    result = cli(
        "sqs",
        "tag-queue",
        "--queue-url",
        queue_url,
        "--tags",
        json.dumps(expected_tags),
    )
    assert result.returncode == 0

    after = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert after.get("Tags") == expected_tags