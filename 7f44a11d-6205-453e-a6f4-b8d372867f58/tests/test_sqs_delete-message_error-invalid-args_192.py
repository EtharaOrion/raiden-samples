def test_delete_message_invalid_receipt_handle(cli, sqs):
    queue_name = "test-delete-msg-invalid-rh"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a real message so the queue is non-empty state we can verify.
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in sent

    # Attempt to delete with a bogus receipt handle -> service error.
    result = cli(
        "sqs", "delete-message",
        "--queue-url", queue_url,
        "--receipt-handle", "this-is-not-a-valid-receipt-handle",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ReceiptHandleIsInvalid" in result.stderr or "InvalidIdFormat" in result.stderr

    # State: the message was NOT deleted; queue still reports it present.
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })["Attributes"]
    total = int(attrs.get("ApproximateNumberOfMessages", "0")) + \
        int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert total >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})