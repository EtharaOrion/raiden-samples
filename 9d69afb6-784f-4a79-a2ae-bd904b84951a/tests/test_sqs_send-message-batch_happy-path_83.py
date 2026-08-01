import json

def test_send_message_batch_happy_path(cli, sqs):
    queue_name = "smb-happy-path-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    entries = [
        {"Id": "msg1", "MessageBody": "hello one"},
        {"Id": "msg2", "MessageBody": "hello two"},
        {"Id": "msg3", "MessageBody": "hello three"},
    ]

    result = cli(
        "sqs", "send-message-batch",
        "--queue-url", queue_url,
        "--entries", json.dumps(entries),
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    successful_ids = {s["Id"] for s in out["Successful"]}
    assert {"msg1", "msg2", "msg3"} <= successful_ids
    for s in out["Successful"]:
        assert s.get("MessageId")

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) == 3