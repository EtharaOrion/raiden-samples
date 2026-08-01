def test_list_queues_returns_existing_queue(cli, sqs, tmp_path):
    import json
    import uuid

    queue_name = f"list-queues-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith(f"/{queue_name}")

    result = cli("sqs", "list-queues")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert any(
        queue_url.endswith(f"/{queue_name}")
        for queue_url in output.get("QueueUrls", [])
    )

    state = sqs.rpc("ListQueues", {})
    assert any(
        queue_url.endswith(f"/{queue_name}")
        for queue_url in state.get("QueueUrls", [])
    )