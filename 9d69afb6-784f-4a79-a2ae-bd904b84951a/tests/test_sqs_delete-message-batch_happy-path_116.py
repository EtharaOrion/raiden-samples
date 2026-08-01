def test_delete_message_batch_happy_path(cli, sqs, tmp_path):
    import json

    qname = "test-delmsgbatch-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    # Seed messages
    sqs.rpc("SendMessageBatch", {
        "QueueUrl": queue_url,
        "Entries": [
            {"Id": "m1", "MessageBody": "body-one"},
            {"Id": "m2", "MessageBody": "body-two"},
        ],
    })

    # Receive messages to capture real receipt handles
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

    assert len(handles) >= 1

    entries = [{"Id": f"d{i}", "ReceiptHandle": h} for i, h in enumerate(handles)]
    entries_json = json.dumps(entries)

    result = cli(
        "sqs", "delete-message-batch",
        "--queue-url", queue_url,
        "--entries", entries_json,
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    successful_ids = {s["Id"] for s in out.get("Successful", [])}
    for e in entries:
        assert e["Id"] in successful_ids

    # Verify deleted messages are gone: send fresh known message, ensure count reflects deletions
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
    })["Attributes"]
    total = int(attrs.get("ApproximateNumberOfMessages", "0")) + \
            int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert total <= 2 - len(handles)