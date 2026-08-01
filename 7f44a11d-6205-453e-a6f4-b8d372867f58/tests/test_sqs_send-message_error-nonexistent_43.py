def test_send_message_nonexistent_queue(cli, sqs):
    queue_name = "test-nonexistent-send-queue"
    account = "000000000000"
    bogus_url = f"http://localhost:9324/{account}/{queue_name}"

    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    for url in existing.get("QueueUrls", []) or []:
        if url.endswith(queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Attempt to send a message to the nonexistent queue
    result = cli(
        "sqs", "send-message",
        "--queue-url", bogus_url,
        "--message-body", "hello world",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert the queue still does not exist
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith(queue_name) for url in (after.get("QueueUrls", []) or [])
    )