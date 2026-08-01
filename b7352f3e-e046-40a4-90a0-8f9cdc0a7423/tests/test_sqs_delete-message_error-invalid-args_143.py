def test_delete_message_rejects_unknown_flag_without_deleting_message(cli, sqs):
    import hashlib
    import uuid

    queue_name = "delete-invalid-" + uuid.uuid4().hex
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message-must-remain"
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    received = None
    for _ in range(5):
        messages = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        ).get("Messages", [])
        if messages:
            received = messages[0]
            break

    assert received is not None
    assert received["Body"] == body
    assert received["MD5OfBody"] == expected_md5
    receipt_handle = received["ReceiptHandle"]

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        receipt_handle,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    sqs.rpc(
        "ChangeMessageVisibility",
        {
            "QueueUrl": queue_url,
            "ReceiptHandle": receipt_handle,
            "VisibilityTimeout": 0,
        },
    )

    remaining = None
    for _ in range(5):
        messages = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        ).get("Messages", [])
        if messages:
            remaining = messages[0]
            break

    assert remaining is not None
    assert remaining["Body"] == body
    assert remaining["MD5OfBody"] == expected_md5