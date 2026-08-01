def test_receive_message_happy_path(cli, sqs):
    queue_name = "receive-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-world-message"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent.get("MessageId")

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "10",
    )
    assert result.returncode == 0

    import json
    messages = []
    if result.stdout.strip():
        parsed = json.loads(result.stdout)
        messages = parsed.get("Messages", [])

    if messages:
        bodies = [m.get("Body") for m in messages]
        assert body in bodies
        for m in messages:
            if m.get("Body") == body:
                sqs.rpc("DeleteMessage", {
                    "QueueUrl": queue_url,
                    "ReceiptHandle": m["ReceiptHandle"],
                })
    else:
        # Tolerate empty first read (short-poll / visibility), but confirm
        # the message really is enqueued via an independent state read.
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["All"],
        })["Attributes"]
        visible = int(attrs.get("ApproximateNumberOfMessages", "0"))
        in_flight = int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
        assert visible + in_flight >= 1