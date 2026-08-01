def test_delete_message_batch_deletes_received_messages(cli, sqs, tmp_path):
    import hashlib
    import json
    import time
    import uuid

    queue_name = "delete-message-batch-" + uuid.uuid4().hex
    queue = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "1"},
        },
    )
    queue_url = queue["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    expected_by_id = {}
    for body in ("first batch message", "second batch message"):
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        expected_md5 = hashlib.md5(body.encode("utf-8")).hexdigest()
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == expected_md5
        expected_by_id[sent["MessageId"]] = (body, expected_md5)

    received_by_id = {}
    for _ in range(6):
        response = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 1,
            },
        )
        for message in response.get("Messages", []):
            if message["MessageId"] in expected_by_id:
                expected_body, expected_md5 = expected_by_id[message["MessageId"]]
                assert message["Body"] == expected_body
                assert message["MD5OfBody"] == expected_md5
                received_by_id[message["MessageId"]] = message
        if set(received_by_id) == set(expected_by_id):
            break

    assert set(received_by_id) == set(expected_by_id)

    entries = [
        {"Id": "delete-1", "ReceiptHandle": message["ReceiptHandle"]}
        for message in received_by_id.values()
    ]
    entries[1]["Id"] = "delete-2"

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
    assert {item["Id"] for item in output.get("Successful", [])} == {
        "delete-1",
        "delete-2",
    }
    assert output.get("Failed", []) == []

    time.sleep(1.5)
    for _ in range(3):
        remaining = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 1,
            },
        )
        assert not remaining.get("Messages")

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
    assert attributes["ApproximateNumberOfMessages"] == "0"
    assert attributes["ApproximateNumberOfMessagesNotVisible"] == "0"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))