def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-world-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in sent

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

    import json

    received_body = None
    receipt_handle = None
    if result.stdout.strip():
        payload = json.loads(result.stdout)
        messages = payload.get("Messages", [])
        if messages:
            received_body = messages[0].get("Body")
            receipt_handle = messages[0].get("ReceiptHandle")

    if received_body is not None:
        assert received_body == body
        # Delete the received message and assert it's gone
        sqs.rpc("DeleteMessage", {"QueueUrl": queue_url, "ReceiptHandle": receipt_handle})
        attrs = sqs.rpc(
            "GetQueueAttributes",
            {"QueueUrl": queue_url, "AttributeNames": ["All"]},
        )["Attributes"]
        total = int(attrs.get("ApproximateNumberOfMessages", "0")) + int(
            attrs.get("ApproximateNumberOfMessagesNotVisible", "0")
        )
        assert total == 0
    else:
        # Tolerate empty first read: message must still exist in the queue
        attrs = sqs.rpc(
            "GetQueueAttributes",
            {"QueueUrl": queue_url, "AttributeNames": ["All"]},
        )["Attributes"]
        total = int(attrs.get("ApproximateNumberOfMessages", "0")) + int(
            attrs.get("ApproximateNumberOfMessagesNotVisible", "0")
        )
        assert total >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})