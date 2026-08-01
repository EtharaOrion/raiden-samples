def test_receive_message_nonexistent_queue_error(cli, sqs):
    base = sqs.rpc("ListQueues", {}).get("QueueUrls", [])
    if base:
        prefix = base[0].rsplit("/", 1)[0]
    else:
        created = sqs.rpc("CreateQueue", {"QueueName": "seed-queue-xyz"})["QueueUrl"]
        prefix = created.rsplit("/", 1)[0]

    missing_name = "no-such-queue-abc123"
    missing_url = prefix + "/" + missing_name

    # Ensure the queue really does not exist
    urls = sqs.rpc("ListQueues", {}).get("QueueUrls", [])
    assert not any(u.endswith("/" + missing_name) for u in urls)

    result = cli("sqs", "receive-message", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: queue still does not exist
    urls_after = sqs.rpc("ListQueues", {}).get("QueueUrls", [])
    assert not any(u.endswith("/" + missing_name) for u in urls_after)