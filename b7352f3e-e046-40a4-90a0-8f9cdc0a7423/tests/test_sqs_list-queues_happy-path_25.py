def test_list_queues_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:12]
    queue_name = f"list-queues-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith(f"/{queue_name}")

    result = cli("sqs", "list-queues")
    assert result.returncode == 0

    output = json.loads(result.stdout)
    assert any(
        queue_url.endswith(f"/{queue_name}")
        for queue_url in output.get("QueueUrls", [])
    )

    observed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        queue_url.endswith(f"/{queue_name}")
        for queue_url in observed.get("QueueUrls", [])
    )