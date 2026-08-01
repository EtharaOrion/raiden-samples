def test_get_queue_url_returns_existing_queue_url(cli, sqs):
    queue_name = "happy-path-get-url-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    created_url = created["QueueUrl"]
    assert created_url.endswith("/" + queue_name)

    result = cli("sqs", "get-queue-url", "--queue-name", queue_name)
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    returned_url = parsed["QueueUrl"]
    assert returned_url.endswith("/" + queue_name)

    # Independent state read: URL should resolve to the same queue
    fetched = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert fetched["QueueUrl"].endswith("/" + queue_name)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))