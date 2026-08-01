def test_delete_queue_nonexistent_queue_error(cli, sqs):
    queue_name = "test-delete-nonexistent-queue-xyz"
    bogus_url = "http://localhost:9324/000000000000/" + queue_name

    # Ensure the queue does not exist before the test
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in existing)

    # Attempt to delete a queue that does not exist
    result = cli("sqs", "delete-queue", "--queue-url", bogus_url)

    # Must fail
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm no such queue was created as a side-effect
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in after)