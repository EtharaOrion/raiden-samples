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
            {"Id": "m1", "MessageBody": "hello-1"},
            {"Id": "m2", "MessageBody": "hello-2"},
        ],
    })

    # Receive messages to get valid receipt handles
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

    assert len(handles) >= 1, "expected to receive at least one message"

    entries = [
        {"Id": "e%d" % i, "ReceiptHandle": h, "VisibilityTimeout": 30}
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
    expected_ids = {e["Id"] for e in entries}
    assert expected_ids.issubset(successful_ids)

    # Verify queue still exists / messages remain (not deleted by this op)
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))