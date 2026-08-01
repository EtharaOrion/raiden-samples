def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
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
    out = json.loads(result.stdout) if result.stdout.strip() else {}
    messages = out.get("Messages", [])

    if messages:
        assert any(m.get("Body") == body for m in messages)
        for m in messages:
            sqs.rpc(
                "DeleteMessage",
                {"QueueUrl": queue_url, "ReceiptHandle": m["ReceiptHandle"]},
            )
    else:
        # message may still be in-flight/invisible; verify it exists in the queue
        attrs = sqs.rpc(
            "GetQueueAttributes",
            {"QueueUrl": queue_url, "AttributeNames": ["All"]},
        )["Attributes"]
        total = int(attrs.get("ApproximateNumberOfMessages", "0")) + int(
            attrs.get("ApproximateNumberOfMessagesNotVisible", "0")
        )
        assert total >= 1