def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-world-message"
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    sent_id = send["MessageId"]

    received_bodies = []
    received_ids = []
    for _ in range(10):
        result = cli(
            "sqs", "receive-message",
            "--queue-url", queue_url,
            "--max-number-of-messages", "10",
            "--wait-time-seconds", "1",
        )
        assert result.returncode == 0, result.stderr
        if result.stdout.strip():
            import json
            data = json.loads(result.stdout)
            for msg in data.get("Messages", []):
                received_bodies.append(msg["Body"])
                received_ids.append(msg["MessageId"])
        if received_ids:
            break

    assert sent_id in received_ids
    assert body in received_bodies