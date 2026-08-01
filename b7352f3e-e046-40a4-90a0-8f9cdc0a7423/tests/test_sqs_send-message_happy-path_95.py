def test_send_message_delivers_body_to_queue(cli, sqs):
    import hashlib
    import json
    import time
    import uuid

    queue_name = f"send-message-{uuid.uuid4().hex}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]

    before = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "0"

    message_body = f"valid message {uuid.uuid4().hex} café\n"
    expected_md5 = hashlib.md5(message_body.encode("utf-8")).hexdigest()

    result = cli(
        "sqs",
        "send-message",
        "--queue-url",
        queue_url,
        "--message-body",
        message_body,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert output["MessageId"]
    assert output["MD5OfMessageBody"] == expected_md5

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith(f"/{queue_name}") for url in listed.get("QueueUrls", [])
    )

    message_count = None
    for _ in range(10):
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
        )
        message_count = int(
            attributes["Attributes"]["ApproximateNumberOfMessages"]
        )
        if message_count == 1:
            break
        time.sleep(0.1)
    assert message_count == 1

    messages = []
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
            break

    assert len(messages) == 1
    assert messages[0]["MessageId"] == output["MessageId"]
    assert messages[0]["Body"] == message_body
    assert messages[0]["MD5OfBody"] == expected_md5