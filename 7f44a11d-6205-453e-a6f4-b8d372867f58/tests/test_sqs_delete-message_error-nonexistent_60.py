def test_delete_message_nonexistent_queue(cli, sqs):
    queue_name = "test-delete-msg-nonexistent-q"
    # Ensure the queue does not exist by creating and deleting it.
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)
    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})

    # Confirm the queue is gone.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_url not in listed.get("QueueUrls", [])

    # Attempt to delete a message from the now-nonexistent queue.
    result = cli(
        "sqs", "delete-message",
        "--queue-url", queue_url,
        "--receipt-handle", "some-fake-receipt-handle",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the queue still does not exist.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_url not in listed_after.get("QueueUrls", [])