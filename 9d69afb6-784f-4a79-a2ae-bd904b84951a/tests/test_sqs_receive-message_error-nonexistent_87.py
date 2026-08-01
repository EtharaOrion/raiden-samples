def test_receive_message_nonexistent_queue(cli, sqs):
    account_url = None
    existing = sqs.rpc("CreateQueue", {"QueueName": "seed-existing-queue"})
    account_url = existing["QueueUrl"]

    missing_name = "no-such-queue-xyz"
    base = account_url.rsplit("/", 1)[0]
    missing_url = base + "/" + missing_name

    listed = sqs.rpc("ListQueues", {}).get("QueueUrls", [])
    assert not any(u.endswith("/" + missing_name) for u in listed)

    result = cli("sqs", "receive-message", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    listed_after = sqs.rpc("ListQueues", {}).get("QueueUrls", [])
    assert not any(u.endswith("/" + missing_name) for u in listed_after)