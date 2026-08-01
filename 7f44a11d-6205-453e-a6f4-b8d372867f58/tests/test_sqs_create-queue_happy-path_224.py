def test_create_queue_happy_path(cli, sqs):
    queue_name = "test_create_queue_happy_path_q12"

    # Ensure clean state: delete if already present
    try:
        existing = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
        if existing.get("QueueUrl"):
            sqs.rpc("DeleteQueue", {"QueueUrl": existing["QueueUrl"]})
    except Exception:
        pass

    result = cli("sqs", "create-queue", "--queue-name", queue_name)
    assert result.returncode == 0

    # Verify via independent read
    got = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    url = got["QueueUrl"]
    assert url.endswith("/" + queue_name)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))