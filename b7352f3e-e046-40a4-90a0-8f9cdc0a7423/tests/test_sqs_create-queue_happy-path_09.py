def test_create_queue_happy_path(cli, sqs):
    import json
    import uuid

    queue_name = f"test-create-queue-{uuid.uuid4().hex}"

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not before.get("QueueUrls")

    result = cli("sqs", "create-queue", "--queue-name", queue_name)
    assert result.returncode == 0, result.stderr

    output = json.loads(result.stdout)
    assert output["QueueUrl"].endswith("/" + queue_name)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    matching_urls = [
        url for url in listed.get("QueueUrls", [])
        if url.endswith("/" + queue_name)
    ]
    assert len(matching_urls) == 1

    resolved = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert resolved["QueueUrl"].endswith("/" + queue_name)