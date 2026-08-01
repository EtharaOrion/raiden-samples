def test_get_queue_url_existing_queue(cli, sqs, tmp_path):
    import json
    import uuid

    queue_name = f"get-queue-url-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith(f"/{queue_name}")

    result = cli("sqs", "get-queue-url", "--queue-name", queue_name)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["QueueUrl"].endswith(f"/{queue_name}")

    fetched = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert fetched["QueueUrl"].endswith(f"/{queue_name}")

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        queue_url.endswith(f"/{queue_name}")
        for queue_url in listed.get("QueueUrls", [])
    )