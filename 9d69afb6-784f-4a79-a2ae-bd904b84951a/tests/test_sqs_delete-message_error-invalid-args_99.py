def test_delete_message_missing_receipt_handle(cli, sqs, tmp_path):
    queue_name = "test-delete-msg-missing-rh"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a message so the queue is non-trivial
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in send

    # Run delete-message WITHOUT the required --receipt-handle
    result = cli("sqs", "delete-message", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "receipt-handle" in result.stderr.lower() or "ReceiptHandle" in result.stderr

    # State unchanged: message still present
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})