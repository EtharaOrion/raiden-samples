def test_delete_message_invalid_args(cli, sqs):
    queue_name = "test-delete-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in send

    attrs_before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]

    result = cli(
        "sqs", "delete-message",
        "--queue-url", queue_url,
        "--receipt-handle", "some-receipt-handle",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    attrs_after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert attrs_after["ApproximateNumberOfMessages"] == attrs_before["ApproximateNumberOfMessages"]

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})