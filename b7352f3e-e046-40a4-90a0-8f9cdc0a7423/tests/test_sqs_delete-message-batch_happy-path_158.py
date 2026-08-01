def test_delete_message_batch_deletes_received_messages(cli, sqs, tmp_path):
    import hashlib
    import json
    import time

    suffix = hashlib.sha1(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"delete-message-batch-{suffix}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    bodies = ["first batch message", "second batch message"]
    for body in bodies:
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    received = []
    for _ in range(10):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 2 - len(received),
                "WaitTimeSeconds": 1,
            },
        )
        received.extend(response.get("Messages", []))
        if len(received) == 2:
            break

    assert len(received) == 2
    assert {message["Body"] for message in received} == set(bodies)
    for message in received:
        assert message["ReceiptHandle"]
        assert message["MD5OfBody"] == hashlib.md5(
            message["Body"].encode()
        ).hexdigest()

    entries = [
        {"Id": f"message-{index}", "ReceiptHandle": message["ReceiptHandle"]}
        for index, message in enumerate(received, start=1)
    ]

    result = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    expected_ids = {entry["Id"] for entry in entries}
    assert {entry["Id"] for entry in output.get("Successful", [])} == expected_ids
    assert not output.get("Failed")

    attributes = {}
    for _ in range(50):
        attributes = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                    "ApproximateNumberOfMessagesDelayed",
                ],
            },
        )["Attributes"]
        if (
            attributes.get("ApproximateNumberOfMessages", "0") == "0"
            and attributes.get("ApproximateNumberOfMessagesNotVisible", "0") == "0"
            and attributes.get("ApproximateNumberOfMessagesDelayed", "0") == "0"
        ):
            break
        time.sleep(0.1)

    assert attributes.get("ApproximateNumberOfMessages", "0") == "0"
    assert attributes.get("ApproximateNumberOfMessagesNotVisible", "0") == "0"
    assert attributes.get("ApproximateNumberOfMessagesDelayed", "0") == "0"