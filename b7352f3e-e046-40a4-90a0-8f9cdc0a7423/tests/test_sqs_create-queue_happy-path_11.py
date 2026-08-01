def test_create_queue_happy_path(cli, sqs):
    import uuid

    queue_name = f"create-queue-{uuid.uuid4().hex}"

    result = cli("sqs", "create-queue", "--queue-name", queue_name)

    assert result.returncode == 0, result.stderr

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    queue_urls = listed.get("QueueUrls", [])
    assert any(url.endswith(f"/{queue_name}") for url in queue_urls)

    resolved = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert resolved["QueueUrl"].endswith(f"/{queue_name}")