import json

def test_delete_message_batch_happy_path(cli, sqs):
    qname = "test-del-batch-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(qname)

    # Seed messages
    sqs.rpc("SendMessageBatch", {
        "QueueUrl": queue_url,
        "Entries": [
            {"Id": "m1", "MessageBody": "body-one"},
            {"Id": "m2", "MessageBody": "body-two"},
        ],
    })

    # Receive them to get valid receipt handles
    handles = {}
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 10,
            "WaitTimeSeconds": 1,
        })
        for msg in resp.get("Messages", []):
            handles[msg["MessageId"]] = msg["ReceiptHandle"]
        if len(handles) >= 2:
            break

    assert len(handles) >= 2

    entries = [
        {"Id": f"d{i}", "ReceiptHandle": rh}
        for i, rh in enumerate(handles.values())
    ]

    result = cli(
        "sqs", "delete-message-batch",
        "--queue-url", queue_url,
        "--entries", json.dumps(entries),
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    successful_ids = {s["Id"] for s in out.get("Successful", [])}
    for e in entries:
        assert e["Id"] in successful_ids

    # Assert the queue is now empty of these messages
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) == 0