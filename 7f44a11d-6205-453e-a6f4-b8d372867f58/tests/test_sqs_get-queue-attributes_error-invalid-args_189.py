def test_get_queue_attributes_nonexistent_queue_error(cli, sqs, tmp_path):
    queue_name = "nonexistent-queue-for-attrs-test"
    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    for url in existing:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Build a URL for a queue that does not exist
    missing_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli(
        "sqs", "get-queue-attributes",
        "--queue-url", missing_url,
        "--attribute-names", "All",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert the queue truly does not exist in service state
    remaining = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in remaining)