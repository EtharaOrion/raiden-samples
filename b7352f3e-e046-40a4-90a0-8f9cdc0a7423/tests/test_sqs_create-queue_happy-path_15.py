def test_create_queue_happy_path(cli, sqs):
    import json
    import uuid

    queue_name = f"string-v7-{uuid.uuid4().hex}"
    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith(f"/{queue_name}") for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "create-queue", "--queue-name", queue_name)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["QueueUrl"].endswith(f"/{queue_name}")

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    matching_urls = [
        url
        for url in after.get("QueueUrls", [])
        if url.endswith(f"/{queue_name}")
    ]
    assert len(matching_urls) == 1

    resolved = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert resolved["QueueUrl"].endswith(f"/{queue_name}")