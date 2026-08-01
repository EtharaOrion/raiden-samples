def test_receive_message_nonexistent_queue(cli, sqs):
    # Build a queue URL for a queue that does not exist
    existing = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    base = existing[0].rsplit("/", 1)[0] if existing else "http://localhost:9324/000000000000"
    missing_name = "nonexistent-queue-xyz-12345"
    missing_url = base + "/" + missing_name

    # Ensure the queue really doesn't exist
    urls_before = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + missing_name) for u in urls_before)

    # Attempt to receive from the missing queue
    result = cli("sqs", "receive-message", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State unchanged: queue still absent
    urls_after = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + missing_name) for u in urls_after)