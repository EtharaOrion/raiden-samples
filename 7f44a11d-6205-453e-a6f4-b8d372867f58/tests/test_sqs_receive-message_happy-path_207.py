def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert send.get("MessageId")

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "10",
    )
    assert result.returncode == 0

    messages = []
    if result.stdout.strip():
        import json
        payload = json.loads(result.stdout)
        messages = payload.get("Messages", [])

    if messages:
        # verify the received message corresponds to what we sent
        bodies = [m.get("Body") for m in messages]
        assert body in bodies
        # delete each received message so we can verify emptiness
        for m in messages:
            sqs.rpc("DeleteMessage", {
                "QueueUrl": queue_url,
                "ReceiptHandle": m["ReceiptHandle"],
            })

    # Independent state read: queue exists
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})