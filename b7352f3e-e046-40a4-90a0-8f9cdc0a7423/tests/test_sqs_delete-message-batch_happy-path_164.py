def test_delete_message_batch_deletes_received_messages(cli, sqs, tmp_path):
    import hashlib
    import json
    import time

    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )
    queue_name = ("delete-message-batch-" + suffix)[-80:]

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    bodies = ["first batch message", "second batch message"]
    expected_md5 = {}
    for body in bodies:
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()
        expected_md5[body] = sent["MD5OfMessageBody"]

    received_messages = []
    for _ in range(5):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 1,
            },
        )
        received_messages.extend(response.get("Messages", []))
        if len(received_messages) == len(bodies):
            break

    assert len(received_messages) == len(bodies)
    assert {message["Body"] for message in received_messages} == set(bodies)
    for message in received_messages:
        assert message["MessageId"]
        assert message["ReceiptHandle"]
        assert message["MD5OfBody"] == expected_md5[message["Body"]]

    for _ in range(10):
        before = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )["Attributes"]
        if int(before.get("ApproximateNumberOfMessagesNotVisible", "0")) == len(bodies):
            break
        time.sleep(0.1)

    assert int(before.get("ApproximateNumberOfMessagesNotVisible", "0")) == len(bodies)

    entries = [
        {"Id": "delete-1", "ReceiptHandle": received_messages[0]["ReceiptHandle"]},
        {"Id": "delete-2", "ReceiptHandle": received_messages[1]["ReceiptHandle"]},
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
    assert {entry["Id"] for entry in output.get("Successful", [])} == {
        "delete-1",
        "delete-2",
    }
    assert output.get("Failed", []) == []

    for _ in range(10):
        after = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": [
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                ],
            },
        )["Attributes"]
        remaining = int(after.get("ApproximateNumberOfMessages", "0"))
        in_flight = int(after.get("ApproximateNumberOfMessagesNotVisible", "0"))
        if remaining == 0 and in_flight == 0:
            break
        time.sleep(0.1)

    assert remaining == 0
    assert in_flight == 0