def test_list_queues_returns_existing_queue(cli, sqs, tmp_path):
    import json

    unique = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-40:]
    queue_name = f"list-queues-{unique}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith("/" + queue_name)

    result = cli("sqs", "list-queues")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output.get("QueueUrls"), list)
    assert any(url.endswith("/" + queue_name) for url in output["QueueUrls"])

    current_state = sqs.rpc("ListQueues", {})
    assert any(
        url.endswith("/" + queue_name)
        for url in current_state.get("QueueUrls", [])
    )