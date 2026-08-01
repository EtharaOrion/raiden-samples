def test_change_message_visibility_batch_makes_messages_visible(cli, sqs, tmp_path):
    import hashlib
    import json
    import uuid

    queue_name = f"visibility-batch-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "120"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    expected_bodies = {
        "first batch message",
        "second batch message",
    }
    for body in expected_bodies:
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    initially_received = {}
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
            body = message["Body"]
            assert body in expected_bodies
            assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
            initially_received[body] = message
        if set(initially_received) == expected_bodies:
            break

    assert set(initially_received) == expected_bodies

    entries = [
        {
            "Id": f"entry-{index}",
            "ReceiptHandle": initially_received[body]["ReceiptHandle"],
            "VisibilityTimeout": 0,
        }
        for index, body in enumerate(sorted(expected_bodies), start=1)
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
    assert {item["Id"] for item in output["Successful"]} == {
        entry["Id"] for entry in entries
    }
    assert not output.get("Failed")

    visible_after_change = set()
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
            body = message["Body"]
            assert body in expected_bodies
            assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
            visible_after_change.add(body)
            sqs.rpc(
                "DeleteMessage",
                {
                    "QueueUrl": queue_url,
                    "ReceiptHandle": message["ReceiptHandle"],
                },
            )
        if visible_after_change == expected_bodies:
            break

    assert visible_after_change == expected_bodies