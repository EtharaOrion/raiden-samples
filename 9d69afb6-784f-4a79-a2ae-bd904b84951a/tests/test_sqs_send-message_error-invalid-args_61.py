def test_send_message_missing_required_queue_url(cli, sqs):
    queue_name = "test-send-missing-queue-url"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "0"

    result = cli("sqs", "send-message", "--message-body", "hello world")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "queue-url" in result.stderr.lower()

    after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "0"