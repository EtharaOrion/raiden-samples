def test_send_message_batch_nonexistent_queue(cli, sqs):
    import json
    import uuid

    token = "batch-nonexistent-" + uuid.uuid4().hex
    existing_name = token + "-existing"
    missing_name = token + "-missing"

    created = sqs.rpc("CreateQueue", {"QueueName": existing_name})
    existing_url = created["QueueUrl"]
    assert existing_url.endswith("/" + existing_name)

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": token}).get("QueueUrls", [])
    assert any(url.endswith("/" + existing_name) for url in before)
    assert not any(url.endswith("/" + missing_name) for url in before)

    missing_url = existing_url.rsplit("/", 1)[0] + "/" + missing_name
    entries = json.dumps([{"Id": "entry-1", "MessageBody": "must-not-be-sent"}])

    result = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        missing_url,
        "--entries",
        entries,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "QueueDoesNotExist" in result.stderr

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": token}).get("QueueUrls", [])
    assert any(url.endswith("/" + existing_name) for url in after)
    assert not any(url.endswith("/" + missing_name) for url in after)