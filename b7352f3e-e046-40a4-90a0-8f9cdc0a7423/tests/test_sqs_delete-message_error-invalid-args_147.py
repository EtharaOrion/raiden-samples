def test_delete_message_rejects_unknown_attribute_definitions(cli, sqs, tmp_path):
    queue_name = "delete-invalid-" + tmp_path.name[-30:]
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message must remain after argument validation failure"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"]

    received = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 1,
        },
    ).get("Messages", [])
    if not received:
        received = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        ).get("Messages", [])

    assert len(received) == 1
    message = received[0]
    assert message["Body"] == body
    assert message["MD5OfBody"] == sent["MD5OfMessageBody"]
    receipt_handle = message["ReceiptHandle"]

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
        },
    )["Attributes"]
    assert int(before["ApproximateNumberOfMessagesNotVisible"]) == 1

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        receipt_handle,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
        },
    )["Attributes"]
    assert int(after["ApproximateNumberOfMessagesNotVisible"]) == 1

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith("/" + queue_name) for url in listed)