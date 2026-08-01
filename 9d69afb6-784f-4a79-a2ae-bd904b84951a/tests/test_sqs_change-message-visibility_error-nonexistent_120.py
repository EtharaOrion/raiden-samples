def test_change_message_visibility_nonexistent_queue(cli, sqs):
    # Create a real queue to derive a valid URL shape, then delete it so it is gone.
    created = sqs.rpc("CreateQueue", {"QueueName": "cmv-nonexistent-test-q"})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/cmv-nonexistent-test-q")

    # Delete the queue so it no longer exists.
    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})

    # Confirm it is gone.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": "cmv-nonexistent-test-q"})
    assert queue_url not in listed.get("QueueUrls", [])

    # Attempt to change visibility on the now-missing queue.
    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", queue_url,
        "--receipt-handle", "some-bogus-receipt-handle",
        "--visibility-timeout", "30",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: queue still does not exist.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": "cmv-nonexistent-test-q"})
    assert queue_url not in listed_after.get("QueueUrls", [])