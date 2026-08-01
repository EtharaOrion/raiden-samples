def test_change_message_visibility_batch_makes_received_messages_visible(cli, sqs, tmp_path):
    import hashlib
    import json
    import uuid

    queue_name = f"visibility-batch-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    expected_bodies = {"first batch message", "second batch message"}
    for body in expected_bodies:
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    initially_received = {}
    for _ in range(10):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 1,
            },
        )
        for message in response.get("Messages", []):
            initially_received[message["Body"]] = message
        if set(initially_received) == expected_bodies:
            break

    assert set(initially_received) == expected_bodies

    entries = []
    for index, body in enumerate(sorted(expected_bodies)):
        entries.append(
            {
                "Id": f"message-{index}",
                "ReceiptHandle": initially_received[body]["ReceiptHandle"],
                "VisibilityTimeout": 0,
            }
        )

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
    assert {item["Id"] for item in output.get("Successful", [])} == {
        entry["Id"] for entry in entries
    }
    assert not output.get("Failed")

    visible_again = {}
    for _ in range(10):
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
        if set(visible_again) == expected_bodies:
            break

    assert set(visible_again) == expected_bodies
    for body, message in visible_again.items():
        assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
        assert message["MessageId"] == initially_received[body]["MessageId"]