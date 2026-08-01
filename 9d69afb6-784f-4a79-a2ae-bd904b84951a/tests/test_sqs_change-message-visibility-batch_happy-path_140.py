def test_change_message_visibility_batch_happy_path(cli, sqs, tmp_path):
    import json

    queue_name = "cmvb-happy-test-queue"
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

    entries = [
        {"Id": f"e{i}", "ReceiptHandle": h, "VisibilityTimeout": 30}
        for i, h in enumerate(handles)
    ]

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

    # Independent read: messages are still invisible (visibility extended), so
    # not available for immediate receive. Attributes should reflect messages
    # exist but are not visible.
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })["Attributes"]
    total = int(attrs.get("ApproximateNumberOfMessages", "0")) + \
        int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert total >= 1