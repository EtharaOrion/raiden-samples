def test_send_message_missing_message_body_fails(cli, sqs, tmp_path):
    queue_name = "test-missing-body-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Run send-message WITHOUT the required --message-body
    result = cli("sqs", "send-message", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "message-body" in result.stderr.lower() or "messagebody" in result.stderr.lower()

    # Assert no message was actually enqueued
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert attrs["Attributes"]["ApproximateNumberOfMessages"] == "0"