def test_send_message_batch_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json
    import uuid

    queue_name = f"send-message-batch-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "0"

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
    successful = {item["Id"]: item for item in output.get("Successful", [])}
    assert set(successful) == {"first", "second"}
    assert not output.get("Failed")
    for entry in entries:
        sent = successful[entry["Id"]]
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(
            entry["MessageBody"].encode("utf-8")
        ).hexdigest()

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "2"