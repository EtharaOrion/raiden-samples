def test_delete_message_batch_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json
    import time
    import uuid

    queue_name = f"delete-message-batch-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "5"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message to delete in a batch"
    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    message = None
    for _ in range(5):
        received = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        messages = received.get("Messages", [])
        if messages:
            message = messages[0]
            break

    assert message is not None
    assert message["Body"] == body
    assert message["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
    assert message["ReceiptHandle"]

    result = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(
            [
                {
                    "Id": "delete-1",
                    "ReceiptHandle": message["ReceiptHandle"],
                }
            ]
        ),
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert {entry["Id"] for entry in output.get("Successful", [])} == {"delete-1"}
    assert not output.get("Failed", [])

    time.sleep(5.2)
    after = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 1,
        },
    )
    assert not after.get("Messages", [])