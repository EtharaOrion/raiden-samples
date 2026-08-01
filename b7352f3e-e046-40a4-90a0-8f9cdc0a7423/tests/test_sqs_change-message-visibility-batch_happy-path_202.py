def test_change_message_visibility_batch_makes_messages_immediately_visible(cli, sqs):
    import hashlib
    import json
    import time
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

    bodies = ["visibility batch message one", "visibility batch message two"]
    for body in bodies:
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    received_by_body = {}
    deadline = time.monotonic() + 10
    while len(received_by_body) < len(bodies) and time.monotonic() < deadline:
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 2,
                "WaitTimeSeconds": 1,
            },
        )
        for message in response.get("Messages", []):
            assert message["Body"] in bodies
            assert message["MD5OfBody"] == hashlib.md5(
                message["Body"].encode()
            ).hexdigest()
            received_by_body[message["Body"]] = message

    assert set(received_by_body) == set(bodies)

    baseline = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 10,
            "WaitTimeSeconds": 0,
        },
    )
    assert not baseline.get("Messages")

    entries = [
        {
            "Id": f"entry-{index}",
            "ReceiptHandle": received_by_body[body]["ReceiptHandle"],
            "VisibilityTimeout": 0,
        }
        for index, body in enumerate(bodies, start=1)
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
    assert {item["Id"] for item in output.get("Successful", [])} == {
        entry["Id"] for entry in entries
    }
    assert not output.get("Failed")

    visible_bodies = set()
    deadline = time.monotonic() + 10
    while visible_bodies != set(bodies) and time.monotonic() < deadline:
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 2,
                "WaitTimeSeconds": 1,
            },
        )
        for message in response.get("Messages", []):
            assert message["Body"] in bodies
            assert message["MD5OfBody"] == hashlib.md5(
                message["Body"].encode()
            ).hexdigest()
            visible_bodies.add(message["Body"])

    assert visible_bodies == set(bodies)