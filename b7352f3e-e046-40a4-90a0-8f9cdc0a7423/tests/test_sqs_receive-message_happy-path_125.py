def test_receive_message_returns_seeded_message_and_makes_it_invisible(cli, sqs, tmp_path):
    import hashlib
    import json
    import time

    queue_name = "receive-" + hashlib.sha256(
        str(tmp_path).encode("utf-8")
    ).hexdigest()[:16]
    body = "black-box receive-message payload"

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {
                "VisibilityTimeout": "30",
                "ReceiveMessageWaitTimeSeconds": "5",
            },
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"] == expected_md5

    deadline = time.monotonic() + 5
    while True:
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["ApproximateNumberOfMessages"],
            },
        )["Attributes"]
        if int(attributes.get("ApproximateNumberOfMessages", "0")) >= 1:
            break
        assert time.monotonic() < deadline
        time.sleep(0.05)

    result = cli("sqs", "receive-message", "--queue-url", queue_url)

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert len(output["Messages"]) == 1
    message = output["Messages"][0]
    assert message["MessageId"] == sent["MessageId"]
    assert message["Body"] == body
    assert message["MD5OfBody"] == expected_md5
    assert message["ReceiptHandle"]

    subsequent = sqs.rpc(
        "ReceiveMessage",
        {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 0,
        },
    )
    assert not subsequent.get("Messages")