def test_receive_message_happy_path(cli, sqs):
    queue_name = "test_receive_happy_v4"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in sent

    # Ensure message is enqueued before receiving
    for _ in range(10):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })
        if attrs["Attributes"].get("ApproximateNumberOfMessages") == "1":
            break

    import json
    received_body = None
    receipt_handle = None
    for _ in range(10):
        result = cli(
            "sqs", "receive-message",
            "--queue-url", queue_url,
            "--max-number-of-messages", "1",
            "--wait-time-seconds", "1",
        )
        assert result.returncode == 0
        if result.stdout.strip():
            out = json.loads(result.stdout)
            msgs = out.get("Messages", [])
            if msgs:
                received_body = msgs[0]["Body"]
                receipt_handle = msgs[0]["ReceiptHandle"]
                break

    assert received_body == body
    assert receipt_handle

    # Confirm we can delete the received message (valid handle)
    sqs.rpc("DeleteMessage", {"QueueUrl": queue_url, "ReceiptHandle": receipt_handle})

    for _ in range(10):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        })
        if attrs["Attributes"].get("ApproximateNumberOfMessages") == "0":
            break
    assert attrs["Attributes"].get("ApproximateNumberOfMessages") == "0"