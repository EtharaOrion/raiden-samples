def test_receive_message_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json
    import time

    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )
    queue_name = ("receive-message-" + suffix)[:80]
    body = "message available for receive-message"

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "120"},
        },
    )
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
    assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    received = None
    for _ in range(5):
        result = cli("sqs", "receive-message", "--queue-url", queue_url)
        assert result.returncode == 0
        output = json.loads(result.stdout)
        messages = output.get("Messages", [])
        if messages:
            received = messages[0]
            break
        time.sleep(0.2)

    assert received is not None
    assert received["MessageId"] == sent["MessageId"]
    assert received["Body"] == body
    assert received["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
    assert received["ReceiptHandle"]

    independently_received = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 1,
        },
    )
    assert not independently_received.get("Messages")

    deadline = time.monotonic() + 5
    while True:
        attributes = sqs.rpc(
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
            attributes["ApproximateNumberOfMessages"] == "0"
            and attributes["ApproximateNumberOfMessagesNotVisible"] == "1"
        ):
            break
        assert time.monotonic() < deadline
        time.sleep(0.1)