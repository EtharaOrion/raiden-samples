def test_get_queue_attributes_nonexistent(cli, sqs):
    queue_name = "nonexistent-queue-xyz-12345"
    missing_url = "http://localhost:9324/000000000000/" + queue_name

    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert missing_url not in existing

    result = cli("sqs", "get-queue-attributes", "--queue-url", missing_url,
                 "--attribute-names", "All")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist
    still_missing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert missing_url not in still_missing