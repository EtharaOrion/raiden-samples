def test_receive_message_nonexistent_queue_errors(cli, sqs):
    # Prerequisite: ensure a valid baseline queue exists, then target a missing one.
    existing = sqs.rpc("CreateQueue", {"QueueName": "test-recv-baseline-q"})
    existing_url = existing["QueueUrl"]
    assert existing_url.endswith("/test-recv-baseline-q")

    # Build a queue URL that does not exist by swapping the queue name.
    missing_url = existing_url.rsplit("/", 1)[0] + "/test-recv-missing-q"

    # Confirm the missing queue truly is absent.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": "test-recv-missing-q"})
    assert missing_url not in listed.get("QueueUrls", [])

    # Run the command under test against the non-existent queue.
    result = cli("sqs", "receive-message", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the missing queue was not created as a side effect.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": "test-recv-missing-q"})
    assert missing_url not in listed_after.get("QueueUrls", [])