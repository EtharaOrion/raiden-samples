def test_change_message_visibility_happy_path(cli, sqs):
    queue_name = "cmv-happy-test-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello-cmv"})
    assert send.get("MessageId")

    # Receive the message to obtain a valid receipt handle
    receipt_handle = None
    for _ in range(5):
        recv = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1})
        msgs = recv.get("Messages") or []
        if msgs:
            receipt_handle = msgs[0]["ReceiptHandle"]
            break
    assert receipt_handle is not None

    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", queue_url,
        "--receipt-handle", receipt_handle,
        "--visibility-timeout", "60",
    )
    assert result.returncode == 0

    # The message remains invisible (in flight) after extending visibility.
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
    })["Attributes"]
    assert attrs["ApproximateNumberOfMessagesNotVisible"] == "1"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})