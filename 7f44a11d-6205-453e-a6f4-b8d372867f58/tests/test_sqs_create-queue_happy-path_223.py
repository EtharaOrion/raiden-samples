def test_create_queue_happy_path(cli, sqs):
    queue_name = "test_string_v7_happy_queue"

    # Ensure clean state: delete if it already exists
    try:
        existing = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
        if existing.get("QueueUrl"):
            sqs.rpc("DeleteQueue", {"QueueUrl": existing["QueueUrl"]})
    except Exception:
        pass

    # Run command under test
    result = cli("sqs", "create-queue", "--queue-name", queue_name)
    assert result.returncode == 0

    # Assert resulting state via independent read
    got = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    queue_url = got["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))

    # Cleanup
    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})