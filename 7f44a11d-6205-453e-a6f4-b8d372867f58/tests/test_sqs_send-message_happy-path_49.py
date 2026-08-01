def test_send_message_delivers_body_to_queue(cli, sqs):
    queue_name = "test-send-message-happy-path-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello world {\"json\":true} <xml/>"
    result = cli("sqs", "send-message", "--queue-url", queue_url,
                 "--message-body", body)
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    assert "MessageId" in out and out["MessageId"]

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) == 1

    seen_body = None
    for _ in range(5):
        recv = sqs.rpc("ReceiveMessage", {
            "QueueUrl": queue_url,
            "MaxNumberOfMessages": 1,
            "WaitTimeSeconds": 1,
        })
        msgs = recv.get("Messages") or []
        if msgs:
            seen_body = msgs[0]["Body"]
            break
    assert seen_body == body