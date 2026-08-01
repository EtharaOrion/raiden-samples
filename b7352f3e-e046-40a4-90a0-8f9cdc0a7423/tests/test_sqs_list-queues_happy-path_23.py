def test_list_queues_returns_existing_queue(cli, sqs, tmp_path):
    import json

    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )[:40]
    queue_name = f"list-queues-{suffix}"

    sqs.rpc("CreateQueue", {"QueueName": queue_name})

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