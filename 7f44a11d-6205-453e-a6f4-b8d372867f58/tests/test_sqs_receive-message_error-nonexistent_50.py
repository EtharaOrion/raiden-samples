def test_receive_message_nonexistent_queue(cli, sqs):
    queue_name = "nonexistent-queue-xyz-123"
    account = "000000000000"
    bad_url = f"http://localhost:9324/{account}/{queue_name}"

    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in existing)

    result = cli("sqs", "receive-message", "--queue-url", bad_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in after)