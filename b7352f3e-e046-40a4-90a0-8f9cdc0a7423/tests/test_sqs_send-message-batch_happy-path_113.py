def test_send_message_batch_happy_path(cli, sqs):
    import json
    import uuid

    queue_name = f"send-message-batch-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    entries = [
        {"Id": "first", "MessageBody": "batch message one"},
        {"Id": "second", "MessageBody": "batch message two"},
    ]

    result = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    successful = {item["Id"]: item for item in output["Successful"]}
    assert set(successful) == {"first", "second"}
    assert all(successful[entry_id].get("MessageId") for entry_id in successful)

    expected_by_body = {
        entry["MessageBody"]: successful[entry["Id"]] for entry in entries
    }
    received_by_body = {}

    for _ in range(5):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 2,
            },
        )
        for message in response.get("Messages", []):
            received_by_body[message["Body"]] = message
        if set(received_by_body) == set(expected_by_body):
            break

    assert set(received_by_body) == set(expected_by_body)
    for body, message in received_by_body.items():
        batch_result = expected_by_body[body]
        assert message["MessageId"] == batch_result["MessageId"]
        assert message["MD5OfBody"] == batch_result["MD5OfMessageBody"]