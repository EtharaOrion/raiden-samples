def test_delete_queue_error_nonexistent(cli, sqs):
    queue_name = "nonexistent-queue-xyz-123"
    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert not any(u.endswith("/" + queue_name) for u in existing)

    # Construct a plausible-looking but nonexistent queue URL
    queue_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Verify the queue still does not exist
    still = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert not any(u.endswith("/" + queue_name) for u in still)