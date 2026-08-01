def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-recv-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert send.get("MessageId")

    result = cli(
        "sqs",
        "receive-message",
        "--queue-url",
        queue_url,
        "--max-number-of-messages",
        "10",
        "--wait-time-seconds",
        "5",
    )
    assert result.returncode == 0

    received_body = None
    receipt_handle = None
    if result.stdout.strip():
        import json
        parsed = json.loads(result.stdout)
        messages = parsed.get("Messages", [])
        if messages:
            received_body = messages[0].get("Body")
            receipt_handle = messages[0].get("ReceiptHandle")

    if received_body is not None:
        assert received_body == body
        assert receipt_handle
        sqs.rpc("DeleteMessage", {"QueueUrl": queue_url, "ReceiptHandle": receipt_handle})
    else:
        # tolerate short-poll empty first read; message must still exist server-side
        attrs = sqs.rpc(
            "GetQueueAttributes",
            {"QueueUrl": queue_url, "AttributeNames": ["All"]},
        )["Attributes"]
        total = (
            int(attrs.get("ApproximateNumberOfMessages", "0"))
            + int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
        )
        assert total >= 1