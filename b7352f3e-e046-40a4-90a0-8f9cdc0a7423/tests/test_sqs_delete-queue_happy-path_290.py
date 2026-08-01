def test_delete_queue_removes_existing_queue(cli, sqs):
    import time
    import uuid

    queue_name = f"delete-queue-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name) for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    for _ in range(20):
        after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
        if not any(
            url.endswith("/" + queue_name) for url in after.get("QueueUrls", [])
        ):
            break
        time.sleep(0.1)

    assert not any(
        url.endswith("/" + queue_name) for url in after.get("QueueUrls", [])
    )