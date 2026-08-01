def test_send_message_error_nonexistent(cli, sqs):
    # Build a queue URL for a queue that does not exist
    existing = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    base = existing[0].rsplit("/", 1)[0] if existing else "http://localhost:9324/000000000000"
    missing_name = "nonexistent-queue-abc123xyz"
    missing_url = base + "/" + missing_name

    # Ensure it truly does not exist
    urls = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + missing_name) for u in urls)

    result = cli(
        "sqs", "send-message",
        "--queue-url", missing_url,
        "--message-body", "hello",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist
    urls = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + missing_name) for u in urls)