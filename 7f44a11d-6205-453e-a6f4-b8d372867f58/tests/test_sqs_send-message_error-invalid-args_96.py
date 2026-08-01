def test_send_message_nonexistent_queue_error(cli, sqs):
    account = "000000000000"
    queue_name = "nonexistent-queue-for-send-test"
    bogus_url = f"http://localhost:9324/{account}/{queue_name}"

    # Ensure the queue does not exist.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    for url in listed.get("QueueUrls", []) or []:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    result = cli(
        "sqs", "send-message",
        "--queue-url", bogus_url,
        "--message-body", "hello world",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist (no side effect).
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name)
        for u in (listed_after.get("QueueUrls", []) or [])
    )