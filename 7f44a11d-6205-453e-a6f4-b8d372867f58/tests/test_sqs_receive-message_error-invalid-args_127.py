def test_receive_message_nonexistent_queue_error(cli, sqs):
    # Establish a known-good queue first, then derive a URL for a queue that does not exist.
    real = sqs.rpc("CreateQueue", {"QueueName": "recv-err-base"})
    base_url = real["QueueUrl"]
    assert base_url.endswith("/recv-err-base")

    # Build a URL for a queue that was never created (same account path, different name).
    missing_url = base_url.rsplit("/", 1)[0] + "/recv-err-missing-queue"

    # Sanity: the missing queue is not present.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": "recv-err-missing-queue"})
    assert missing_url not in listed.get("QueueUrls", [])

    result = cli("sqs", "receive-message", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # The missing queue still does not exist after the failed call.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": "recv-err-missing-queue"})
    assert missing_url not in listed_after.get("QueueUrls", [])