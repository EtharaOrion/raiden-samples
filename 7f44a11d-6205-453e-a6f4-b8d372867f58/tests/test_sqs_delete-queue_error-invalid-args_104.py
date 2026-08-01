def test_delete_queue_nonexistent_queue_errors(cli, sqs):
    account = "000000000000"
    queue_name = "definitely-missing-queue-xyz"
    bogus_url = f"http://localhost:9324/{account}/{queue_name}"

    # Ensure the queue does not exist beforehand.
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in existing)

    result = cli("sqs", "delete-queue", "--queue-url", bogus_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State: the queue still does not exist.
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in after)