def test_list_queue_tags_returns_existing_tags(cli, sqs):
    import json
    import uuid

    queue_name = f"list-queue-tags-{uuid.uuid4().hex}"
    tags = {
        "environment": "test",
        "component": "payments",
    }

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": tags})

    result = cli("sqs", "list-queue-tags", "--queue-url", queue_url)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Tags"] == tags

    observed = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert observed["Tags"] == tags