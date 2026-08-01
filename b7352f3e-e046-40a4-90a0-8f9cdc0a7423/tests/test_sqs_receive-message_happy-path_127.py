def test_receive_message_returns_seeded_message_and_makes_it_invisible(cli, sqs, tmp_path):
    import hashlib
    import json

    queue_name = "receive-happy-" + tmp_path.name
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {
                "ReceiveMessageWaitTimeSeconds": "2",
                "VisibilityTimeout": "30",
            },
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "black-box receive-message payload"
    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": body,
        },
    )
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli("sqs", "receive-message", "--queue-url", queue_url)

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output["Messages"]) == 1
    message = output["Messages"][0]
    assert message["MessageId"] == sent["MessageId"]
    assert message["Body"] == body
    assert message["MD5OfBody"] == expected_md5
    assert message["ReceiptHandle"]

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
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "0"
    assert after["Attributes"]["ApproximateNumberOfMessagesNotVisible"] == "1"

    second_read = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 0,
        },
    )
    assert not second_read.get("Messages")