def test_change_message_visibility_batch_makes_messages_visible(cli, sqs, tmp_path):
    import hashlib
    import json
    import time

    suffix = "".join(c for c in tmp_path.name if c.isalnum() or c in "-_")[-40:]
    queue_name = "visibility-batch-" + suffix

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    bodies = ["visibility-message-one", "visibility-message-two"]
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
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 1,
            },
        )
        for message in response.get("Messages", []):
            body = message["Body"]
            assert body in bodies
            assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
            received_by_body[body] = message

    assert set(received_by_body) == set(bodies)

    invisible = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 10,
            "WaitTimeSeconds": 0,
        },
    )
    assert not invisible.get("Messages")

    entries = [
        {
            "Id": "message-one",
            "ReceiptHandle": received_by_body[bodies[0]]["ReceiptHandle"],
            "VisibilityTimeout": 0,
        },
        {
            "Id": "message-two",
            "ReceiptHandle": received_by_body[bodies[1]]["ReceiptHandle"],
            "VisibilityTimeout": 0,
        },
    ]

    result = cli(
        "sqs",
        "change-message-visibility-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert {item["Id"] for item in output.get("Successful", [])} == {
        "message-one",
        "message-two",
    }
    assert not output.get("Failed")

    visible_bodies = set()
    deadline = time.monotonic() + 10
    while visible_bodies != set(bodies) and time.monotonic() < deadline:
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
            assert body in bodies
            assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
            visible_bodies.add(body)

    assert visible_bodies == set(bodies)