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

    observed = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert observed["QueueUrl"].endswith(f"/{queue_name}")