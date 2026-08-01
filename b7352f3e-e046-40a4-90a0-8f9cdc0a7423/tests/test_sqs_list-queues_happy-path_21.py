def test_list_queues_returns_existing_queue(cli, sqs, tmp_path):
    import json

    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )
    queue_name = f"list-queues-{suffix}"[:80]

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith("/" + queue_name)

    result = cli("sqs", "list-queues")

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output.get("QueueUrls"), list)
    assert any(url.endswith("/" + queue_name) for url in output["QueueUrls"])

    current = sqs.rpc("ListQueues", {})
    assert any(
        url.endswith("/" + queue_name)
        for url in current.get("QueueUrls", [])
    )