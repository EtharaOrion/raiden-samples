def test_untag_queue_nonexistent_queue(cli, sqs):
    account = "000000000000"
    queue_name = "nonexistent-untag-queue-xyz"
    bogus_url = f"http://localhost:9324/{account}/{queue_name}"

    # Ensure the queue does not exist
    try:
        existing = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
        url = existing.get("QueueUrl")
        if url:
            sqs.rpc("DeleteQueue", {"QueueUrl": url})
    except Exception:
        pass

    result = cli(
        "sqs", "untag-queue",
        "--queue-url", bogus_url,
        "--tag-keys", '["foo"]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm queue still absent
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls") or []
    assert not any(u.endswith(f"/{queue_name}") for u in urls)