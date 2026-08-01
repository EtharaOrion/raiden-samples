def test_delete_message_batch_rejects_too_many_entries(cli, sqs, tmp_path):
    import hashlib
    import json
    import uuid

    queue_name = "delete-batch-too-many-" + uuid.uuid4().hex
    queue = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "0"},
        },
    )
    queue_url = queue["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message-must-survive-rejected-batch"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    received = None
    for _ in range(5):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        messages = response.get("Messages", [])
        if messages:
            received = messages[0]
            break

    assert received is not None
    assert received["Body"] == body
    assert received["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()

    entries = [
        {"Id": "entry-0", "ReceiptHandle": received["ReceiptHandle"]}
    ] + [
        {"Id": f"entry-{index}", "ReceiptHandle": f"invalid-handle-{index}"}
        for index in range(1, 11)
    ]

    result = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "TooManyEntriesInBatchRequest" in result.stderr

    surviving = None
    for _ in range(5):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        messages = response.get("Messages", [])
        if messages:
            surviving = messages[0]
            break

    assert surviving is not None
    assert surviving["Body"] == body
    assert surviving["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()