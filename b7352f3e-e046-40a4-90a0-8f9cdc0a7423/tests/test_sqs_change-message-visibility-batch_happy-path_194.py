def test_change_message_visibility_batch_makes_messages_visible(cli, sqs, tmp_path):
    import hashlib
    import json
    import uuid

    queue_name = f"visibility-batch-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    bodies = ["first batch message", "second batch message"]
    for body in bodies:
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

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
        if set(received_by_body) == set(bodies):
            break

    assert set(received_by_body) == set(bodies)
    for body, message in received_by_body.items():
        assert message["ReceiptHandle"]
        assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()

    before = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 10,
            "WaitTimeSeconds": 0,
        },
    )
    assert not before.get("Messages")

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

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert {item["Id"] for item in output.get("Successful", [])} == {
        entry["Id"] for entry in entries
    }
    assert not output.get("Failed")

    visible_after = {}
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
            visible_after[message["Body"]] = message
        if set(visible_after) == set(bodies):
            break

    assert set(visible_after) == set(bodies)
    for body, message in visible_after.items():
        assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()