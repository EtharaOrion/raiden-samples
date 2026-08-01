def test_delete_message_batch_happy_path(cli, sqs):
    import json

    queue_name = "test-delete-msg-batch-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed messages
    batch = sqs.rpc("SendMessageBatch", {
        "QueueUrl": queue_url,
        "Entries": [
            {"Id": "m1", "MessageBody": "body-one"},
            {"Id": "m2", "MessageBody": "body-two"},
        ],
    })
    sent_ids = {s["Id"] for s in batch["Successful"]}
    assert sent_ids == {"m1", "m2"}

    # Receive the messages to obtain valid receipt handles
    handles = []
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 10,
            "WaitTimeSeconds": 1,
        })
        for msg in resp.get("Messages", []):
            handles.append(msg["ReceiptHandle"])
        if len(handles) >= 2:
            break
    assert len(handles) >= 2

    entries = [
        {"Id": "d1", "ReceiptHandle": handles[0]},
        {"Id": "d2", "ReceiptHandle": handles[1]},
    ]

    result = cli(
        "sqs", "delete-message-batch",
        "--queue-url", queue_url,
        "--entries", json.dumps(entries),
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    successful_ids = {s["Id"] for s in out.get("Successful", [])}
    assert {"d1", "d2"} <= successful_ids

    # Verify state: queue should now be drained
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert attrs["Attributes"]["ApproximateNumberOfMessages"] == "0"