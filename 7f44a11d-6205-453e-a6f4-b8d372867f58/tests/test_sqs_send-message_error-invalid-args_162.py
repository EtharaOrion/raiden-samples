def test_send_message_nonexistent_queue_error(cli, sqs, tmp_path):
    queue_name = "throttle-test-queue-abc123"
    # Ensure the queue does not exist by deleting it if present
    try:
        url = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})["QueueUrl"]
        sqs.rpc("DeleteQueue", {"QueueUrl": url})
    except Exception:
        pass

    # Construct a URL that points at a non-existent queue
    bogus_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli(
        "sqs", "send-message",
        "--queue-url", bogus_url,
        "--message-body", "hello world",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert state: the queue still does not exist
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in urls)