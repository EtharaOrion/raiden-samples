def test_get_queue_url_nonexistent_queue_errors(cli, sqs):
    queue_name = "nonexistent-queue-for-geturl-test"

    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    for url in existing.get("QueueUrls", []) or []:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    result = cli("sqs", "get-queue-url", "--queue-name", queue_name)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist in state
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in (after.get("QueueUrls", []) or [])
    )