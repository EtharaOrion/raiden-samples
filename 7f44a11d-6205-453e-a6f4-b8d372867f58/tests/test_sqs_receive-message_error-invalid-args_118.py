def test_receive_message_nonexistent_queue(cli, sqs):
    queue_name = "test-receive-missing-queue-xyz"
    base = sqs.rpc("ListQueues", {}).get("QueueUrls", [])
    existing = [u for u in base if u.endswith("/" + queue_name)]
    assert not existing, "precondition: queue must not exist"

    fake_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli("sqs", "receive-message", "--queue-url", fake_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    after = sqs.rpc("ListQueues", {}).get("QueueUrls", [])
    assert not [u for u in after if u.endswith("/" + queue_name)]