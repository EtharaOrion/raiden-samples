def test_change_message_visibility_batch_happy_path(cli, sqs):
    qname = "cmvb-happy-test-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    # Seed messages
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "msg-a"})
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "msg-b"})

    # Receive them to obtain valid receipt handles
    handles = []
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 10})
        for m in resp.get("Messages", []):
            handles.append(m["ReceiptHandle"])
        if len(handles) >= 2:
            break

    assert len(handles) >= 1, "expected at least one received message"

    entries = [
        {"Id": f"e{i}", "ReceiptHandle": h, "VisibilityTimeout": 30}
        for i, h in enumerate(handles)
    ]

    import json
    result = cli(
        "sqs", "change-message-visibility-batch",
        "--queue-url", queue_url,
        "--entries", json.dumps(entries),
    )

    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)
    successful_ids = {s["Id"] for s in out.get("Successful", [])}
    for e in entries:
        assert e["Id"] in successful_ids

    # State assertion: messages are now invisible (extended visibility timeout)
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessagesNotVisible"]) >= len(entries)