def test_delete_message_invalid_receipt_handle(cli, sqs, tmp_path):
    queue_name = "test-delete-invalid-handle-q"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a real message so the queue is non-empty
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in send

    # Attempt to delete with a bogus receipt handle
    result = cli(
        "sqs", "delete-message",
        "--queue-url", queue_url,
        "--receipt-handle", "this-is-not-a-valid-receipt-handle",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ReceiptHandleIsInvalid" in result.stderr

    # Assert the message was NOT removed (queue still has its message)
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    count = int(attrs["Attributes"]["ApproximateNumberOfMessages"])
    assert count == 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})