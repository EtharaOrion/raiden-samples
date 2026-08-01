def test_change_message_visibility_invalid_flag(cli, sqs, tmp_path):
    queue_name = "test-cmv-invalid-flag-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(queue_name)

    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in sent

    received = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1, "WaitTimeSeconds": 1})
    messages = received.get("Messages", [])
    receipt_handle = messages[0]["ReceiptHandle"] if messages else "dummy-handle"

    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", queue_url,
        "--receipt-handle", receipt_handle,
        "--visibility-timeout", "30",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    # Queue should still exist and be unaffected
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith(queue_name) for u in listed.get("QueueUrls", []))