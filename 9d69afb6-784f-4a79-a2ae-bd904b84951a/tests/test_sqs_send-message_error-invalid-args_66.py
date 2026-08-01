def test_send_message_invalid_args(cli, sqs):
    queue_name = "test-send-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs", "send-message",
        "--queue-url", queue_url,
        "--message-body", "hello",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    # Assert the message was NOT delivered — queue remains empty
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert attrs["Attributes"]["ApproximateNumberOfMessages"] == "0"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})