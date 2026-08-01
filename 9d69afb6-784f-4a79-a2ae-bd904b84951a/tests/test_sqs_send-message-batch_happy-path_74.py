import json

def test_send_message_batch_happy_path(cli, sqs):
    queue_name = "test-smb-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
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
    successful = out.get("Successful", [])
    success_ids = {s["Id"] for s in successful}
    assert {"msg1", "msg2", "msg3"} <= success_ids
    for s in successful:
        assert s.get("MessageId")

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) == 3