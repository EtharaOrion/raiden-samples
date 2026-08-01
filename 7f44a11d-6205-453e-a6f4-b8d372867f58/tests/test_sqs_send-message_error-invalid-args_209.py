def test_send_message_nonexistent_queue_error(cli, sqs):
    account = "000000000000"
    queue_name = "test-send-missing-queue-abc123"
    bogus_url = f"http://localhost:9324/{account}/{queue_name}"

    # Ensure the queue does NOT exist as prerequisite state.
    listing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    for url in listing.get("QueueUrls", []) or []:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    listing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in (listing.get("QueueUrls", []) or [])
    )

    # Attempt to send a message to the missing queue.
    result = cli(
        "sqs",
        "send-message",
        "--queue-url",
        bogus_url,
        "--message-body",
        "hello world",
    )

    # Must fail with the service error category surfaced in stderr.
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist (no side-effect creation).
    listing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in (listing.get("QueueUrls", []) or [])
    )