def test_send_message_nonexistent_queue_error(cli, sqs):
    account = "000000000000"
    queue_name = "test-send-missing-queue"
    bogus_url = f"http://localhost:9324/{account}/{queue_name}"

    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    for url in existing:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Send a message to a queue that does not exist
    result = cli(
        "sqs", "send-message",
        "--queue-url", bogus_url,
        "--message-body", "hello",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert the queue was NOT created as a side effect
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in after)