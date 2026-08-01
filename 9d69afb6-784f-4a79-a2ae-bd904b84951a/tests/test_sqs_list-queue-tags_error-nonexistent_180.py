def test_list_queue_tags_error_nonexistent(cli, sqs):
    # Ensure the target queue does not exist
    missing_name = "nonexistent-queue-for-tags-test"
    missing_url = "http://localhost:9324/000000000000/" + missing_name

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    for url in listed.get("QueueUrls", []) or []:
        if url.rstrip("/").endswith(missing_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    result = cli("sqs", "list-queue-tags", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue really is absent in service state
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert not any(
        u.rstrip("/").endswith(missing_name)
        for u in (listed_after.get("QueueUrls", []) or [])
    )