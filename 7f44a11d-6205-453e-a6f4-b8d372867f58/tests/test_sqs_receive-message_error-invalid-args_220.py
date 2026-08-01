def test_receive_message_nonexistent_queue_error(cli, sqs):
    # Establish baseline: ensure the target queue name does not exist
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": "nonexistent-recv-queue"})
    for url in existing.get("QueueUrls", []) or []:
        if url.endswith("/nonexistent-recv-queue"):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Build a well-formed but non-existent queue URL
    ref = sqs.rpc("CreateQueue", {"QueueName": "recv-ref-queue"})
    ref_url = ref["QueueUrl"]
    assert ref_url.endswith("/recv-ref-queue")
    # Derive a sibling URL pointing to a queue that does not exist
    bad_url = ref_url.rsplit("/", 1)[0] + "/nonexistent-recv-queue"

    # Run the command under test against the missing queue
    result = cli("sqs", "receive-message", "--queue-url", bad_url)

    # Must fail with an error category surfaced in stderr
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert resulting state: the queue still does not exist
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": "nonexistent-recv-queue"})
    assert not any(
        u.endswith("/nonexistent-recv-queue")
        for u in (after.get("QueueUrls", []) or [])
    )