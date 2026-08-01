def test_delete_queue_error_nonexistent(cli, sqs):
    queue_name = "nonexistent-queue-xyz-12345"
    missing_url = f"http://localhost:9324/000000000000/{queue_name}"

    # Ensure the queue does not exist beforehand
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert not any(u.endswith("/" + queue_name) for u in existing)

    result = cli("sqs", "delete-queue", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert not any(u.endswith("/" + queue_name) for u in after)