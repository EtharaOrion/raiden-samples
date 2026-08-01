def test_list_queue_tags_returns_existing_tags(cli, sqs):
    import json
    import uuid

    queue_name = f"list-queue-tags-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    expected_tags = {
        "environment": "test",
        "owner": "black-box",
    }
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": expected_tags})

    result = cli("sqs", "list-queue-tags", "--queue-url", queue_url)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Tags"] == expected_tags

    state = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert state["Tags"] == expected_tags