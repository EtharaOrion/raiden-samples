import json

def test_delete_message_batch_happy_path(cli, sqs, tmp_path):
    queue_name = "dmb-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed messages
    sqs.rpc("SendMessageBatch", {
        "QueueUrl": queue_url,
        "Entries": [
            {"Id": "m1", "MessageBody": "body-one"},
            {"Id": "m2", "MessageBody": "body-two"},
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

    assert len(handles) >= 1, "expected to receive at least one seeded message"

    entries = [{"Id": "d%d" % i, "ReceiptHandle": h} for i, h in enumerate(handles)]
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

    # Assert resulting queue state: deleted messages should not reappear
    remaining = 0
    for _ in range(5):
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages",
                               "ApproximateNumberOfMessagesNotVisible"],
        })["Attributes"]
        remaining = int(attrs.get("ApproximateNumberOfMessages", "0")) + \
                    int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
        if remaining <= (2 - len(handles)):
            break

    # The messages we deleted are gone; at most the ones we never received remain
    assert remaining <= (2 - len(handles))