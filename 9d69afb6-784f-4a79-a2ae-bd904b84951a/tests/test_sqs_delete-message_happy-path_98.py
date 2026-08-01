def test_delete_message_happy_path(cli, sqs):
    queue_name = "test-delete-msg-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello-delete-me"})

    receipt_handle = None
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1, "WaitTimeSeconds": 1})
        msgs = resp.get("Messages") or []
        if msgs:
            receipt_handle = msgs[0]["ReceiptHandle"]
            break
    assert receipt_handle is not None, "did not receive the seeded message"

    result = cli("sqs", "delete-message", "--queue-url", queue_url, "--receipt-handle", receipt_handle)
    assert result.returncode == 0

    attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": queue_url, "AttributeNames": ["All"]})["Attributes"]
    total = (
        int(attrs.get("ApproximateNumberOfMessages", "0"))
        + int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    )
    assert total == 0