def test_receive_message_returns_seeded_message(cli, sqs):
    import hashlib
    import json
    import uuid

    queue_name = f"receive-message-{uuid.uuid4().hex}"
    queue = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {
                "ReceiveMessageWaitTimeSeconds": "1",
                "VisibilityTimeout": "30",
            },
        },
    )
    queue_url = queue["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "black-box receive-message payload"
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    received_message = None
    for _ in range(3):
        result = cli("sqs", "receive-message", "--queue-url", queue_url)
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout) if result.stdout.strip() else {}
        messages = output.get("Messages", [])
        if messages:
            received_message = messages[0]
            break

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
    for _ in range(3):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        messages = response.get("Messages", [])
        if messages:
            independently_received = messages[0]
            break

    assert independently_received is not None
    assert independently_received["MessageId"] == sent["MessageId"]
    assert independently_received["Body"] == body
    assert independently_received["MD5OfBody"] == expected_md5