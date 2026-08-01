def test_change_message_visibility_happy_path(cli, sqs):
    qname = "cmv-happy-queue-v4"
    create = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello-cmv"})
    assert "MessageId" in send

    # Receive to obtain a valid receipt handle
    receipt = None
    for _ in range(10):
        recv = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1})
        msgs = recv.get("Messages") or []
        if msgs:
            receipt = msgs[0]["ReceiptHandle"]
            break
    assert receipt is not None, "expected to receive a message"

    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", queue_url,
        "--receipt-handle", receipt,
        "--visibility-timeout", "30",
    )
    assert result.returncode == 0, result.stderr

    # The message is still inflight (not deleted); queue still contains it.
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })["Attributes"]
    total = int(attrs.get("ApproximateNumberOfMessages", "0")) + \
        int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert total >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})