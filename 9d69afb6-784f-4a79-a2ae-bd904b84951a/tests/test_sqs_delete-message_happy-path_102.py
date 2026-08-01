def test_delete_message_happy_path(cli, sqs):
    queue_name = "test-delete-msg-happy"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello-delete"})

    # Receive the message to obtain a valid receipt handle
    receipt = None
    for _ in range(10):
        recv = sqs.rpc("ReceiveMessage", {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 1,
        })
        msgs = recv.get("Messages") or []
        if msgs:
            receipt = msgs[0]["ReceiptHandle"]
            break
    assert receipt is not None, "expected to receive a message"

    result = cli("sqs", "delete-message",
                 "--queue-url", queue_url,
                 "--receipt-handle", receipt)
    assert result.returncode == 0

    # Assert the message is gone: queue should drain to 0
    count = None
    for _ in range(10):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages",
                               "ApproximateNumberOfMessagesNotVisible"],
        })["Attributes"]
        visible = int(attrs.get("ApproximateNumberOfMessages", "0"))
        not_visible = int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
        count = visible + not_visible
        if count == 0:
            break
    assert count == 0

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})