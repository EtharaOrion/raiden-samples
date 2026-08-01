def test_change_message_visibility_happy_path(cli, sqs):
    qname = "cmv-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello-cmv"})

    received = None
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1})
        msgs = resp.get("Messages", [])
        if msgs:
            received = msgs[0]
            break
    assert received is not None, "expected to receive the sent message"
    receipt_handle = received["ReceiptHandle"]

    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", queue_url,
        "--receipt-handle", receipt_handle,
        "--visibility-timeout", "0",
    )
    assert result.returncode == 0, result.stderr

    # After setting visibility to 0, the message should become visible again.
    redelivered = None
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1})
        msgs = resp.get("Messages", [])
        if msgs:
            redelivered = msgs[0]
            break
    assert redelivered is not None, "message should be visible again after visibility timeout 0"
    assert redelivered["Body"] == "hello-cmv"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})