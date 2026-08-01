def test_send_message_batch_missing_entries(cli, sqs):
    queue_name = "test-send-batch-missing-entries-q"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Record baseline message count before the (expected-to-fail) command.
    before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    before_count = int(before["Attributes"]["ApproximateNumberOfMessages"])

    # Invoke send-message-batch WITHOUT the required --entries option.
    result = cli("sqs", "send-message-batch", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "entries" in result.stderr.lower()

    # Assert no message was enqueued as a result of the failed command.
    after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    after_count = int(after["Attributes"]["ApproximateNumberOfMessages"])
    assert after_count == before_count

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})