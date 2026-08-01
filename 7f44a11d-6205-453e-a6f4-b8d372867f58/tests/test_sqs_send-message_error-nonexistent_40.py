def test_send_message_error_nonexistent(cli, sqs):
    queue_name = "nonexistent-queue-for-send-test"

    # Ensure the queue does not exist by deleting it if present
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    for url in existing.get("QueueUrls", []) or []:
        if url.endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Construct a URL for a queue that does not exist
    listed = sqs.rpc("ListQueues", {})
    sample_url = None
    for url in listed.get("QueueUrls", []) or []:
        sample_url = url
        break
    if sample_url is not None:
        base = sample_url.rsplit("/", 1)[0]
        missing_url = base + "/" + queue_name
    else:
        missing_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli(
        "sqs", "send-message",
        "--queue-url", missing_url,
        "--message-body", "hello world",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert the queue still does not exist
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in (after.get("QueueUrls", []) or [])
    )