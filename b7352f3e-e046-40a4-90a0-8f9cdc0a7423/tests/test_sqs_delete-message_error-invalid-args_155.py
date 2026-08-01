def test_delete_message_invalid_receipt_handle_preserves_queue_message(cli, sqs, tmp_path):
    queue_name = f"delete-invalid-{abs(hash(str(tmp_path)))}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "message-for-stale-handle"},
    )

    received_messages = []
    for _ in range(3):
        received = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        received_messages = received.get("Messages", [])
        if received_messages:
            break

    assert len(received_messages) == 1
    stale_receipt_handle = received_messages[0]["ReceiptHandle"]
    sqs.rpc(
        "DeleteMessage",
        {
            "QueueUrl": queue_url,
            "ReceiptHandle": stale_receipt_handle,
        },
    )

    survivor = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "message-that-must-remain"},
    )
    assert survivor.get("MessageId")

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        stale_receipt_handle,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ReceiptHandleIsInvalid" in result.stderr

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert attributes["Attributes"]["ApproximateNumberOfMessages"] == "1"