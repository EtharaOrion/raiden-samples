def test_list_queue_tags_returns_existing_tags(cli, sqs, tmp_path):
    import json
    import uuid

    queue_name = f"list-queue-tags-{uuid.uuid4().hex}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    expected_tags = {
        "environment": "test",
        "owner": tmp_path.name,
    }
    sqs.rpc("TagQueue", {"QueueUrl": queue_url, "Tags": expected_tags})

    result = cli("sqs", "list-queue-tags", "--queue-url", queue_url)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Tags"] == expected_tags

    state = sqs.rpc("ListQueueTags", {"QueueUrl": queue_url})
    assert state["Tags"] == expected_tags
    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith(f"/{queue_name}") for url in queues)