def test_delete_message_batch_rejects_unknown_flag_without_deleting(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = "".join(c if c.isalnum() else "-" for c in tmp_path.name)
    queue_name = ("delete-batch-invalid-" + suffix)[-80:]
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message must survive invalid command arguments"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    received_message = None
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
            received_message = messages[0]
            break

    assert received_message is not None
    assert received_message["Body"] == body
    assert received_message["MD5OfBody"] == expected_md5

    entries = json.dumps(
        [
            {
                "Id": "message-1",
                "ReceiptHandle": received_message["ReceiptHandle"],
            }
        ]
    )
    result = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        entries,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    sqs.rpc(
        "ChangeMessageVisibility",
        {
            "QueueUrl": queue_url,
            "ReceiptHandle": received_message["ReceiptHandle"],
            "VisibilityTimeout": 0,
        },
    )

    surviving_message = None
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
            surviving_message = messages[0]
            break

    assert surviving_message is not None
    assert surviving_message["MessageId"] == sent["MessageId"]
    assert surviving_message["Body"] == body
    assert surviving_message["MD5OfBody"] == expected_md5