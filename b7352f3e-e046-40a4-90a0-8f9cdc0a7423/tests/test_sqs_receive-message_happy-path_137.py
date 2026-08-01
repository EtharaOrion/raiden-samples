def test_receive_message_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json
    import time
    import uuid

    queue_name = "receive-message-" + uuid.uuid4().hex
    body = "message-" + uuid.uuid4().hex

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode("utf-8")).hexdigest()

    for _ in range(20):
        before = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )
        if int(before["Attributes"].get("ApproximateNumberOfMessages", "0")) >= 1:
            break
        time.sleep(0.1)
    assert int(before["Attributes"].get("ApproximateNumberOfMessages", "0")) >= 1

    received_message = None
    for _ in range(3):
        result = cli("sqs", "receive-message", "--queue-url", queue_url)
        assert result.returncode == 0
        output = json.loads(result.stdout) if result.stdout.strip() else {}
        messages = output.get("Messages", [])
        if messages:
            received_message = messages[0]
            break

    assert received_message is not None
    assert received_message["MessageId"] == sent["MessageId"]
    assert received_message["Body"] == body
    assert received_message["MD5OfBody"] == hashlib.md5(
        body.encode("utf-8")
    ).hexdigest()

    for _ in range(20):
        after = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )
        attributes = after["Attributes"]
        if (
            int(attributes.get("ApproximateNumberOfMessages", "0")) == 0
            and int(attributes.get("ApproximateNumberOfMessagesNotVisible", "0")) >= 1
        ):
            break
        time.sleep(0.1)

    assert int(after["Attributes"].get("ApproximateNumberOfMessages", "0")) == 0
    assert int(
        after["Attributes"].get("ApproximateNumberOfMessagesNotVisible", "0")
    ) >= 1