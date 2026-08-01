def test_send_message_batch_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json

    queue_name = "send-message-batch-" + tmp_path.name.replace("_", "-")
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

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
    successful = {item["Id"]: item for item in output["Successful"]}
    assert set(successful) == {"first", "second"}
    assert all(successful[entry_id].get("MessageId") for entry_id in successful)
    assert successful["first"]["MD5OfMessageBody"] == hashlib.md5(
        b"first batch message"
    ).hexdigest()
    assert successful["second"]["MD5OfMessageBody"] == hashlib.md5(
        b"second batch message"
    ).hexdigest()
    assert output.get("Failed", []) == []

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "2"