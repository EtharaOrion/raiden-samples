def test_get_queue_attributes_nonexistent_queue(cli, sqs):
    queue_name = "nonexistent-queue-abc123xyz"
    missing_url = "http://localhost:9324/000000000000/" + queue_name

    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert missing_url not in existing
    for url in existing:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    result = cli("sqs", "get-queue-attributes", "--queue-url", missing_url,
                 "--attribute-names", "All")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist in service state
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in after)