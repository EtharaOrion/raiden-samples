def test_change_message_visibility_missing_receipt_handle(cli, sqs, tmp_path):
    import uuid

    queue_name = f"visibility-invalid-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "message remains unchanged"},
    )
    assert sent.get("MessageId")

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli(
        "sqs",
        "change-message-visibility",
        "--queue-url",
        queue_url,
        "--visibility-timeout",
        "10",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--receipt-handle" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"