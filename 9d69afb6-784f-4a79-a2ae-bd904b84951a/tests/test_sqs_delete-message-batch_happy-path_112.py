import json

def test_delete_message_batch_happy_path(cli, sqs, tmp_path):
    qname = "test-dmb-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    # Seed messages
    sqs.rpc("SendMessageBatch", {
        "QueueUrl": queue_url,
        "Entries": [
            {"Id": "m1", "MessageBody": "hello-1"},
            {"Id": "m2", "MessageBody": "hello-2"},
        ],
    })

    # Receive messages to obtain valid receipt handles
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
    assert "d1" in successful_ids
    assert "d2" in successful_ids

    # Assert resulting state: queue drained of these messages
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
    })["Attributes"]
    total = int(attrs.get("ApproximateNumberOfMessages", "0")) + \
        int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert total == 0