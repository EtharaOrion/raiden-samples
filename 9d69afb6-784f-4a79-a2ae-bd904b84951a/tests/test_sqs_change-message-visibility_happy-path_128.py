def test_change_message_visibility_happy_path(cli, sqs):
    qname = "cmv-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello-world"})
    assert send.get("MessageId")

    # Receive the message to obtain a valid receipt handle
    receipt_handle = None
    for _ in range(10):
        recv = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1})
        msgs = recv.get("Messages") or []
        if msgs:
            receipt_handle = msgs[0]["ReceiptHandle"]
            break
    assert receipt_handle, "expected to receive a message to change visibility on"

    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", queue_url,
        "--receipt-handle", receipt_handle,
        "--visibility-timeout", "0",
    )
    assert result.returncode == 0, result.stderr

    # After setting visibility timeout to 0, the message becomes visible again.
    found_again = False
    for _ in range(10):
        recv = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 1})
        msgs = recv.get("Messages") or []
        if msgs and msgs[0]["Body"] == "hello-world":
            found_again = True
            break
    assert found_again, "message should be receivable again after visibility timeout reset to 0"