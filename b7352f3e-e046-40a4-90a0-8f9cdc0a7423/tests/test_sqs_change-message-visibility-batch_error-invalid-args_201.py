def test_change_message_visibility_batch_rejects_invalid_arguments(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )
    queue_name = ("invalid-visibility-batch-" + suffix)[-80:]

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "message must remain visible after argument validation fails"
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    assert attributes["Attributes"]["ApproximateNumberOfMessages"] == "1"

    received = None
    for _ in range(10):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        if response.get("Messages"):
            received = response["Messages"][0]
            break

    assert received is not None
    assert received["Body"] == body
    assert received["MD5OfBody"] == sent["MD5OfMessageBody"]

    sqs.rpc(
        "ChangeMessageVisibility",
        {
            "QueueUrl": queue_url,
            "ReceiptHandle": received["ReceiptHandle"],
            "VisibilityTimeout": 0,
        },
    )

    entries = json.dumps(
        [
            {
                "Id": "entry-1",
                "ReceiptHandle": received["ReceiptHandle"],
                "VisibilityTimeout": 300,
            }
        ]
    )
    result = cli(
        "sqs",
        "change-message-visibility-batch",
        "--queue-url",
        queue_url,
        "--entries",
        entries,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    visible_again = None
    for _ in range(10):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 1,
                "WaitTimeSeconds": 1,
            },
        )
        if response.get("Messages"):
            visible_again = response["Messages"][0]
            break

    assert visible_again is not None
    assert visible_again["Body"] == body
    assert visible_again["MD5OfBody"] == sent["MD5OfMessageBody"]

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))