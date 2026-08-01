def test_create_queue_happy_path(cli, sqs, tmp_path):
    import uuid

    queue_name = f"create-queue-{uuid.uuid4().hex}"
    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith(f"/{queue_name}") for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "create-queue", "--queue-name", queue_name)
    assert result.returncode == 0

    created = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith(f"/{queue_name}") for url in after.get("QueueUrls", [])
    )