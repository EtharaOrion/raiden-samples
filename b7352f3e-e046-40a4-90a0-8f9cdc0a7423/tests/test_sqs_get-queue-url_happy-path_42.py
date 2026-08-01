def test_get_queue_url_existing_queue(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"get-queue-url-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith(f"/{queue_name}")

    result = cli("sqs", "get-queue-url", "--queue-name", queue_name)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["QueueUrl"].endswith(f"/{queue_name}")

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith(f"/{queue_name}") for url in queues)