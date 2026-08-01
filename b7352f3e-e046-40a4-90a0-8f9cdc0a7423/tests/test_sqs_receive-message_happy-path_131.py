def test_receive_message_returns_seeded_message_and_hides_it(cli, sqs):
    import hashlib
    import json
    import time
    import uuid

    queue_name = f"receive-message-{uuid.uuid4().hex}"
    queue_url = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "black-box receive-message payload"
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    visible = None
    for _ in range(20):
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )["Attributes"]
        visible = int(attributes.get("ApproximateNumberOfMessages", "0"))
        if visible == 1:
            break
        time.sleep(0.1)
    assert visible == 1

    result = cli("sqs", "receive-message", "--queue-url", queue_url)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    messages = output.get("Messages", [])
    assert len(messages) == 1
    assert messages[0]["MessageId"] == sent["MessageId"]
    assert messages[0]["Body"] == body
    assert messages[0]["MD5OfBody"] == expected_md5
    assert messages[0]["ReceiptHandle"]

    resulting_attributes = None
    for _ in range(20):
        resulting_attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )["Attributes"]
        if (
            resulting_attributes.get("ApproximateNumberOfMessages") == "0"
            and resulting_attributes.get("ApproximateNumberOfMessagesNotVisible") == "1"
        ):
            break
        time.sleep(0.1)

    assert resulting_attributes["ApproximateNumberOfMessages"] == "0"
    assert resulting_attributes["ApproximateNumberOfMessagesNotVisible"] == "1"