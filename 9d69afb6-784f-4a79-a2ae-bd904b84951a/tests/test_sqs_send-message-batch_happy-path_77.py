import json

def test_send_message_batch_happy_path(cli, sqs):
    queue_name = "test-smb-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    entries = [
        {"Id": "msg1", "MessageBody": "hello world"},
        {"Id": "msg2", "MessageBody": "goodbye world"},
        {"Id": "msg3", "MessageBody": "another message"},
    ]

    result = cli(
        "sqs", "send-message-batch",
        "--queue-url", queue_url,
        "--entries", json.dumps(entries),
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    successful_ids = {s["Id"] for s in out.get("Successful", [])}
    for e in entries:
        assert e["Id"] in successful_ids
    for s in out.get("Successful", []):
        assert s.get("MessageId")

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    count = int(attrs["Attributes"]["ApproximateNumberOfMessages"])
    assert count == len(entries)