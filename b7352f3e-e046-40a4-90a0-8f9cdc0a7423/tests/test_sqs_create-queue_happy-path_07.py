def test_create_queue_happy_path(cli, sqs, tmp_path):
    import json
    import uuid

    queue_name = f"create-queue-{uuid.uuid4().hex}"

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith("/" + queue_name) for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "create-queue", "--queue-name", queue_name)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["QueueUrl"].endswith("/" + queue_name)

    queue = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert queue["QueueUrl"].endswith("/" + queue_name)

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name) for url in after.get("QueueUrls", [])
    )