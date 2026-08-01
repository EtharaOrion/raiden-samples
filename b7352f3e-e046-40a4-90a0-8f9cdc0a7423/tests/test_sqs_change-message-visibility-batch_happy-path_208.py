def test_change_message_visibility_batch_makes_received_messages_visible(cli, sqs, tmp_path):
    import hashlib
    import json

    queue_name = "visibility-batch-" + hashlib.sha256(
        str(tmp_path).encode("utf-8")
    ).hexdigest()[:16]
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "60"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    bodies = {
        "first": "first visibility batch message",
        "second": "second visibility batch message",
    }
    for body in bodies.values():
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(
            body.encode("utf-8")
        ).hexdigest()

    received_by_body = {}
    for _ in range(5):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 1,
            },
        )
        for message in response.get("Messages", []):
            received_by_body[message["Body"]] = message
        if set(received_by_body) == set(bodies.values()):
            break

    assert set(received_by_body) == set(bodies.values())

    baseline = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 10,
            "WaitTimeSeconds": 1,
        },
    )
    assert not baseline.get("Messages")

    entries = [
        {
            "Id": entry_id,
            "ReceiptHandle": received_by_body[body]["ReceiptHandle"],
            "VisibilityTimeout": 0,
        }
        for entry_id, body in bodies.items()
    ]
    result = cli(
        "sqs",
        "change-message-visibility-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert {item["Id"] for item in output.get("Successful", [])} == set(bodies)
    assert not output.get("Failed")

    visible_again = {}
    for _ in range(5):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 1,
            },
        )
        for message in response.get("Messages", []):
            visible_again[message["Body"]] = message
        if set(visible_again) == set(bodies.values()):
            break

    assert set(visible_again) == set(bodies.values())
    for body, message in visible_again.items():
        assert message["MD5OfBody"] == hashlib.md5(
            body.encode("utf-8")
        ).hexdigest()