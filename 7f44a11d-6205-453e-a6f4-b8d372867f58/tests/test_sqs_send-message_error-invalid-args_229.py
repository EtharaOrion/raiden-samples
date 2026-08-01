def test_send_message_nonexistent_queue_error(cli, sqs):
    queue_name = "test-send-msg-missing-queue"
    # Ensure the queue does not exist by deleting it if present
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    for url in existing.get("QueueUrls", []) or []:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Confirm absence
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in (listed.get("QueueUrls", []) or [])
    )

    bogus_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli(
        "sqs", "send-message",
        "--queue-url", bogus_url,
        "--message-body", "hello",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: queue still does not exist
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in (listed_after.get("QueueUrls", []) or [])
    )