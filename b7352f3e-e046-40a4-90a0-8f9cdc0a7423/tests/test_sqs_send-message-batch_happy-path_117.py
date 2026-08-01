def test_send_message_batch_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json
    import time
    import uuid

    queue_name = f"send-message-batch-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    entries = [
        {"Id": "first", "MessageBody": "first batch message"},
        {"Id": "second", "MessageBody": "second batch message"},
    ]

    result = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    successful = {item["Id"]: item for item in output.get("Successful", [])}
    assert set(successful) == {"first", "second"}
    assert output.get("Failed", []) == []

    for entry in entries:
        sent = successful[entry["Id"]]
        assert sent["MessageId"]
        expected_md5 = hashlib.md5(entry["MessageBody"].encode()).hexdigest()
        assert sent["MD5OfMessageBody"] == expected_md5

    message_count = None
    for _ in range(20):
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )["Attributes"]
        message_count = int(attributes["ApproximateNumberOfMessages"])
        if message_count == len(entries):
            break
        time.sleep(0.1)

    assert message_count == len(entries)