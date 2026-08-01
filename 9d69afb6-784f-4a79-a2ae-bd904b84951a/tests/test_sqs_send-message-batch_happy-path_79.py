def test_send_message_batch_happy_path(cli, sqs):
    queue_name = "smb-happy-test-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    import json

    entries = [
        {"Id": "msg1", "MessageBody": "hello world"},
        {"Id": "msg2", "MessageBody": "second message"},
        {"Id": "msg3", "MessageBody": "third message"},
    ]

    result = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    successful = out.get("Successful", [])
    successful_ids = {s["Id"] for s in successful}
    assert successful_ids == {"msg1", "msg2", "msg3"}
    for s in successful:
        assert s.get("MessageId")

    attrs = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) == 3