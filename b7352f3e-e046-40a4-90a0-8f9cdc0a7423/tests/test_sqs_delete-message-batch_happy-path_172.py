def test_delete_message_batch_deletes_received_messages(cli, sqs, tmp_path):
    import hashlib
    import json
    import time

    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )
    queue_name = ("delete-message-batch-" + suffix)[-80:]

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))

    bodies = ["batch-message-one", "batch-message-two"]
    for body in bodies:
        sent = sqs.rpc(
            "SendMessage",
            {"QueueUrl": queue_url, "MessageBody": body},
        )
        assert sent["MessageId"]
        assert sent["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()

    received_by_body = {}
    for _ in range(5):
        received = sqs.rpc(
            "ReceiveMessage",
            {
                "QueueUrl": queue_url,
                "MaxNumberOfMessages": 10,
                "WaitTimeSeconds": 1,
            },
        )
        for message in received.get("Messages", []):
            assert message["MD5OfBody"] == hashlib.md5(
                message["Body"].encode()
            ).hexdigest()
            received_by_body[message["Body"]] = message
        if set(received_by_body) == set(bodies):
            break

    assert set(received_by_body) == set(bodies)

    entries = [
        {
            "Id": f"entry-{index}",
            "ReceiptHandle": received_by_body[body]["ReceiptHandle"],
        }
        for index, body in enumerate(bodies, start=1)
    ]

    before = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["All"]},
    )
    assert int(before["Attributes"]["ApproximateNumberOfMessagesNotVisible"]) == 2

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
        entry["Id"] for entry in entries
    }
    assert not output.get("Failed", [])

    for _ in range(20):
        after = sqs.rpc(
            "GetQueueAttributes",
            {"QueueUrl": queue_url, "AttributeNames": ["All"]},
        )
        attributes = after["Attributes"]
        if (
            int(attributes["ApproximateNumberOfMessages"]) == 0
            and int(attributes["ApproximateNumberOfMessagesNotVisible"]) == 0
        ):
            break
        time.sleep(0.1)

    assert int(attributes["ApproximateNumberOfMessages"]) == 0
    assert int(attributes["ApproximateNumberOfMessagesNotVisible"]) == 0