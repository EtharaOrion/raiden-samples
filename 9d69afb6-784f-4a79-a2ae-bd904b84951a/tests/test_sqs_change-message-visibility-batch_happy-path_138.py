def test_change_message_visibility_batch_happy_path(cli, sqs):
    qname = "cmvb-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    # Seed messages
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "msg-one"})
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "msg-two"})

    # Receive them to obtain valid receipt handles
    handles = []
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {"QueueUrl": queue_url, "MaxNumberOfMessages": 10})
        for m in resp.get("Messages", []):
            handles.append(m["ReceiptHandle"])
        if len(handles) >= 2:
            break
    assert len(handles) >= 2

    import json
    entries = [
        {"Id": "e1", "ReceiptHandle": handles[0], "VisibilityTimeout": 30},
        {"Id": "e2", "ReceiptHandle": handles[1], "VisibilityTimeout": 60},
    ]

    result = cli(
        "sqs",
        "change-message-visibility-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    successful_ids = {s["Id"] for s in out.get("Successful", [])}
    assert "e1" in successful_ids
    assert "e2" in successful_ids

    # Independent state read: messages remain invisible (in-flight) after the visibility change
    attrs = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessagesNotVisible"]},
    )["Attributes"]
    assert int(attrs["ApproximateNumberOfMessagesNotVisible"]) >= 2