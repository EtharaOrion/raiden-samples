def test_get_queue_url_error_nonexistent(cli, sqs):
    queue_name = "nonexistent-queue-xyz-12345"

    # Ensure the queue does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = existing.get("QueueUrls") or []
    assert not any(u.endswith("/" + queue_name) for u in urls)

    result = cli("sqs", "get-queue-url", "--queue-name", queue_name)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm the queue still does not exist
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    after_urls = after.get("QueueUrls") or []
    assert not any(u.endswith("/" + queue_name) for u in after_urls)