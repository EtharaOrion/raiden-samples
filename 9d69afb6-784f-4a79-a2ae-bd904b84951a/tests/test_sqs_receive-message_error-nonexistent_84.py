def test_receive_message_nonexistent_queue(cli, sqs):
    # Build a queue URL for a queue that does not exist by creating and deleting one.
    queue_name = "test-nonexistent-recv-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})

    # Confirm it is gone before the command under test.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_url not in listed.get("QueueUrls", [])

    # Run the command under test against the missing queue.
    result = cli("sqs", "receive-message", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: queue still does not exist.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_url not in listed_after.get("QueueUrls", [])