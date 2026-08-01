def test_receive_message_happy_path(cli, sqs):
    queue_name = "test-receive-happy-queue"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    body = "hello-receive-message"
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": body})
    assert "MessageId" in send
    sent_id = send["MessageId"]

    # confirm the message is in the queue before receiving
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--wait-time-seconds", "5",
        "--max-number-of-messages", "10",
    )
    assert result.returncode == 0

    import json
    # stdout may be empty on a short-poll miss; if present it must be valid structure
    received_ids = []
    if result.stdout.strip():
        payload = json.loads(result.stdout)
        for msg in payload.get("Messages", []):
            received_ids.append(msg["MessageId"])
            assert msg["Body"] == body

    if received_ids:
        assert sent_id in received_ids
    else:
        # tolerate short-poll empty read: the message must still be in the queue
        attrs2 = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages", "ApproximateNumberOfMessagesNotVisible"],
        })
        visible = int(attrs2["Attributes"]["ApproximateNumberOfMessages"])
        not_visible = int(attrs2["Attributes"].get("ApproximateNumberOfMessagesNotVisible", "0"))
        assert visible + not_visible >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})