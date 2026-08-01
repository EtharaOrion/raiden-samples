def test_list_queues_happy_path(cli, sqs, tmp_path):
    import json

    queue_name = f"list-queues-{abs(hash(str(tmp_path))):x}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith("/" + queue_name)

    result = cli("sqs", "list-queues")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert any(
        url.endswith("/" + queue_name)
        for url in output.get("QueueUrls", [])
    )

    state = sqs.rpc("ListQueues", {})
    assert any(
        url.endswith("/" + queue_name)
        for url in state.get("QueueUrls", [])
    )