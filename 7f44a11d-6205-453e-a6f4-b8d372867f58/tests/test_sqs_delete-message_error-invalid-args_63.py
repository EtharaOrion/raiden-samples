def test_delete_message_missing_receipt_handle(cli, sqs):
    queue_name = "test-delete-msg-missing-rh-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in send

    result = cli("sqs", "delete-message", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "receipt-handle" in result.stderr.lower() or "ReceiptHandle" in result.stderr

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert attrs["Attributes"]["ApproximateNumberOfMessages"] == "1"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})