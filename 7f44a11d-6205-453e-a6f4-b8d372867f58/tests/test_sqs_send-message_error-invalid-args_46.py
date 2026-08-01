def test_send_message_invalid_args(cli, sqs, tmp_path):
    queue_name = "test-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    before_count = int(before["Attributes"]["ApproximateNumberOfMessages"])

    result = cli(
        "sqs", "send-message",
        "--queue-url", queue_url,
        "--message-body", "hello world",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr.lower() or "unknown" in result.stderr.lower() or "argument" in result.stderr.lower()

    after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    after_count = int(after["Attributes"]["ApproximateNumberOfMessages"])
    assert after_count == before_count