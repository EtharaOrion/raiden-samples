def test_delete_message_removes_message_from_queue(cli, sqs):
    queue_name = "test-delete-msg-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello-to-delete"})

    # Receive to obtain a valid receipt handle (retry to tolerate visibility delays)
    receipt = None
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 1,
        })
        msgs = resp.get("Messages") or []
        if msgs:
            receipt = msgs[0]["ReceiptHandle"]
            break
    assert receipt is not None, "expected to receive the seeded message"

    result = cli("sqs", "delete-message",
                 "--queue-url", queue_url,
                 "--receipt-handle", receipt)
    assert result.returncode == 0

    # After deletion the queue should hold no messages
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })["Attributes"]
    total = (int(attrs.get("ApproximateNumberOfMessages", "0"))
             + int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0")))
    assert total == 0

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})