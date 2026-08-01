def test_delete_message_batch_deletes_received_messages(cli, sqs, tmp_path):
    import hashlib
    import json
    import time

    queue_name = "delete-batch-" + format(abs(hash(str(tmp_path))), "x")
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "60"},
        },
    )
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

    received = []
    deadline = time.monotonic() + 10
    while len(received) < len(bodies) and time.monotonic() < deadline:
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": len(bodies),
                "WaitTimeSeconds": 1,
            },
        )
        received.extend(response.get("Messages", []))

    assert len(received) == len(bodies)
    assert {message["Body"] for message in received} == set(bodies)
    for message in received:
        assert message["ReceiptHandle"]
        assert message["MD5OfBody"] == hashlib.md5(
            message["Body"].encode()
        ).hexdigest()

    baseline = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
        },
    )
    assert int(
        baseline["Attributes"]["ApproximateNumberOfMessagesNotVisible"]
    ) == len(received)

    entries = [
        {"Id": "delete-" + str(index), "ReceiptHandle": message["ReceiptHandle"]}
        for index, message in enumerate(received, start=1)
    ]
    result = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert {entry["Id"] for entry in output["Successful"]} == {
        entry["Id"] for entry in entries
    }
    assert output.get("Failed", []) == []

    remaining_invisible = None
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )["Attributes"]
        remaining_visible = int(attributes["ApproximateNumberOfMessages"])
        remaining_invisible = int(
            attributes["ApproximateNumberOfMessagesNotVisible"]
        )
        if remaining_visible == 0 and remaining_invisible == 0:
            break
        time.sleep(0.1)

    assert remaining_visible == 0
    assert remaining_invisible == 0