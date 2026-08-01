def test_send_message_batch_sends_all_entries(cli, sqs):
    import hashlib
    import json
    import uuid

    queue_name = f"batch-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

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

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    successful = {item["Id"]: item for item in output["Successful"]}

    assert set(successful) == {"first", "second"}
    for entry in entries:
        sent = successful[entry["Id"]]
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(
            entry["MessageBody"].encode("utf-8")
        ).hexdigest()

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert attributes["Attributes"]["ApproximateNumberOfMessages"] == "2"