def test_delete_message_happy_path(cli, sqs):
    queue_name = "test-delete-msg-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith(queue_name)

    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello world"})
    assert "MessageId" in send

    # Receive to obtain a receipt handle; tolerate empty first read
    receipt_handle = None
    for _ in range(10):
        recv = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1, "WaitTimeSeconds": 1})
        messages = recv.get("Messages") or []
        if messages:
            receipt_handle = messages[0]["ReceiptHandle"]
            break
    assert receipt_handle is not None

    result = cli("sqs", "delete-message", "--queue-url", queue_url, "--receipt-handle", receipt_handle)
    assert result.returncode == 0

    attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": queue_url, "AttributeNames": ["All"]})
    approx = int(attrs["Attributes"]["ApproximateNumberOfMessages"])
    not_visible = int(attrs["Attributes"].get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert approx == 0
    assert not_visible == 0