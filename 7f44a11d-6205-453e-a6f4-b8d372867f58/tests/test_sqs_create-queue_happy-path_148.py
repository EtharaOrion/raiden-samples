def test_create_queue_happy_path(cli, sqs):
    queue_name = "test_string_v14_queue"

    # Ensure clean state: delete if it already exists
    try:
        existing = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
        if existing.get("QueueUrl"):
            sqs.rpc("DeleteQueue", {"QueueUrl": existing["QueueUrl"]})
    except Exception:
        pass

    result = cli("sqs", "create-queue", "--queue-name", queue_name)
    assert result.returncode == 0

    # Assert stdout structure
    import json
    payload = json.loads(result.stdout)
    assert "QueueUrl" in payload
    assert payload["QueueUrl"].endswith("/" + queue_name)

    # Independent read-back via sqs state
    got = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert got["QueueUrl"].endswith("/" + queue_name)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))