def test_get_queue_attributes_nonexistent_queue_errors(cli, sqs):
    queue_name = "test-gqa-missing-queue"
    # Ensure the queue does not exist by deleting it if present
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    for url in listed.get("QueueUrls", []) or []:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Confirm absence
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in (listed_after.get("QueueUrls", []) or [])
    )

    # Construct a plausible URL for the missing queue
    bogus_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli("sqs", "get-queue-attributes", "--queue-url", bogus_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State still confirms the queue does not exist
    final = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in (final.get("QueueUrls", []) or [])
    )