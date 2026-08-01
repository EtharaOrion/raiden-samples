def test_delete_message_happy_path(cli, sqs):
    queue_name = "test-delete-msg-happy"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello world"})
    assert "MessageId" in send

    receipt_handle = None
    for _ in range(10):
        recv = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1, "WaitTimeSeconds": 1})
        msgs = recv.get("Messages") or []
        if msgs:
            receipt_handle = msgs[0]["ReceiptHandle"]
            break
    assert receipt_handle is not None

    result = cli("sqs", "delete-message", "--queue-url", queue_url, "--receipt-handle", receipt_handle)
    assert result.returncode == 0

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) == 0
    assert int(attrs["ApproximateNumberOfMessagesNotVisible"]) == 0

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})