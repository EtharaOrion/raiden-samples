def test_delete_queue_nonexistent_queue_error(cli, sqs, tmp_path):
    queue_name = "nonexistent-queue-for-delete-test"
    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    for url in existing:
        sqs.rpc("DeleteQueue", {"QueueUrl": url})

    bogus_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli("sqs", "delete-queue", "--queue-url", bogus_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert the queue still does not exist
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert all(not u.endswith("/" + queue_name) for u in after)