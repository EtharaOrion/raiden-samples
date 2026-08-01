def test_purge_queue_nonexistent(cli, sqs):
    # Ensure the queue does not exist by using a unique name and deleting if present
    queue_name = "nonexistent-purge-queue-xyz123"
    account = "000000000000"
    # Build a queue URL for a queue that does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    for url in existing:
        if url.rstrip("/").endswith(queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Confirm it's gone
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.rstrip("/").endswith(queue_name) for u in after)

    bogus_url = f"http://localhost:9324/{account}/{queue_name}"

    result = cli("sqs", "purge-queue", "--queue-url", bogus_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "QueueDoesNotExist" in result.stderr or "NonExistentQueue" in result.stderr

    # State check: queue still does not exist
    still = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.rstrip("/").endswith(queue_name) for u in still)