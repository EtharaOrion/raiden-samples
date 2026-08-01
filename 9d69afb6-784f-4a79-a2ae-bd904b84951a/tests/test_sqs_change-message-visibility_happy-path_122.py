def test_change_message_visibility_happy_path(cli, sqs):
    qname = "cmv-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello-world"})

    receipt = None
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1})
        msgs = resp.get("Messages") or []
        if msgs:
            receipt = msgs[0]["ReceiptHandle"]
            break
    assert receipt is not None

    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", queue_url,
        "--receipt-handle", receipt,
        "--visibility-timeout", "30",
    )
    assert result.returncode == 0

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessagesNotVisible"]) >= 1

    empty = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1})
    assert not (empty.get("Messages") or [])