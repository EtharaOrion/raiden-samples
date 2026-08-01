def test_receive_message_returns_seeded_message(cli, sqs, tmp_path):
    import hashlib
    import json
    import time

    unique = hashlib.sha256(str(tmp_path).encode("utf-8")).hexdigest()[:20]
    queue_name = f"receive-message-{unique}"
    body = f"message-body-{unique}"
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    received_message = None
    for _ in range(10):
        result = cli("sqs", "receive-message", "--queue-url", queue_url)
        assert result.returncode == 0

        output = json.loads(result.stdout) if result.stdout.strip() else {}
        messages = output.get("Messages", [])
        if messages:
            received_message = messages[0]
            break
        time.sleep(0.1)

    assert received_message is not None
    assert received_message["MessageId"] == sent["MessageId"]
    assert received_message["Body"] == body
    assert received_message["MD5OfBody"] == expected_md5
    assert received_message["ReceiptHandle"]

    sqs.rpc(
        "ChangeMessageVisibility",
        {
            "QueueUrl": queue_url,
            "ReceiptHandle": received_message["ReceiptHandle"],
            "VisibilityTimeout": 0,
        },
    )

    independently_received = None
    for _ in range(5):
        state = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        messages = state.get("Messages", [])
        if messages:
            independently_received = messages[0]
            break

    assert independently_received is not None
    assert independently_received["MessageId"] == sent["MessageId"]
    assert independently_received["Body"] == body
    assert independently_received["MD5OfBody"] == expected_md5