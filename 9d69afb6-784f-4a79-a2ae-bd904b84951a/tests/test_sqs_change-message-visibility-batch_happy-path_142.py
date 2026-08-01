def test_change_message_visibility_batch_happy_path(cli, sqs):
    import json

    queue_name = "cmvb-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]

    # Seed messages
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "msg-one"})
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "msg-two"})

    # Receive messages to obtain valid receipt handles
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

    result = cli(
        "sqs",
        "change-message-visibility-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    successful_ids = {s["Id"] for s in out.get("Successful", [])}
    for e in entries:
        assert e["Id"] in successful_ids

    # Verify messages are now invisible (visibility timeout extended) — queue
    # should still report messages as not-visible / present in flight.
    attrs = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["All"]},
    )["Attributes"]
    # The messages we set visibility on are in flight (not visible).
    not_visible = int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert not_visible >= len(handles)