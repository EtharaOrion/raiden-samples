def test_receive_message_nonexistent_queue_errors(cli, sqs):
    # Establish a real queue first, then derive a URL for a queue that does not exist.
    created = sqs.rpc("CreateQueue", {"QueueName": "seed-queue-for-recv-error"})
    real_url = created["QueueUrl"]
    assert real_url.endswith("/seed-queue-for-recv-error")

    # Build a URL pointing at a queue that was never created.
    missing_url = real_url.rsplit("/", 1)[0] + "/does-not-exist-queue"

    # Confirm the target queue truly does not exist in service state.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": "does-not-exist-queue"})
    assert "does-not-exist-queue" not in "".join(listed.get("QueueUrls", []) or [])

    result = cli("sqs", "receive-message", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the missing queue still does not exist after the failed call.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": "does-not-exist-queue"})
    assert "does-not-exist-queue" not in "".join(listed_after.get("QueueUrls", []) or [])