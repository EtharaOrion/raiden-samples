def test_change_message_visibility_edge_zero_makes_immediately_visible(cli, sqs):
    import uuid

    qname = "edge-cmv-zero-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    sqs.rpc("SendMessage", {"QueueUrl": url, "MessageBody": "cmv-zero-body"})

    receipt = None
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {
            "QueueUrl": url,
            "MaxNumberOfMessages": 1,
            "VisibilityTimeout": 60,
        })
        msgs = resp.get("Messages") or []
        if msgs:
            receipt = msgs[0]["ReceiptHandle"]
            break
    assert receipt is not None

    # Set the in-flight message's visibility timeout to 0 — SQS semantics say
    # the message must immediately become available again.
    r = cli(
        "sqs", "change-message-visibility",
        "--queue-url", url,
        "--receipt-handle", receipt,
        "--visibility-timeout", "0",
    )
    assert r.returncode == 0

    reappeared = False
    import time
    for _ in range(10):
        resp = sqs.rpc("ReceiveMessage", {"QueueUrl": url, "MaxNumberOfMessages": 1})
        if resp.get("Messages"):
            assert resp["Messages"][0]["Body"] == "cmv-zero-body"
            reappeared = True
            break
        time.sleep(0.2)
    assert reappeared

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
