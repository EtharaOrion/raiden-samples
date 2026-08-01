import uuid


def test_change_message_visibility_edge_timeout_zero_reissues(cli, sqs):
    qname = "edge-cmv-zero-" + uuid.uuid4().hex[:16]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    body = "cmv-zero-" + uuid.uuid4().hex
    sqs.rpc("SendMessage", {"QueueUrl": url, "MessageBody": body})

    receipt = None
    for _ in range(15):
        resp = sqs.rpc("ReceiveMessage", {
            "QueueUrl": url, "MaxNumberOfMessages": 1,
            "VisibilityTimeout": 30, "WaitTimeSeconds": 1,
        })
        msgs = resp.get("Messages") or []
        if msgs:
            receipt = msgs[0]["ReceiptHandle"]
            break
    assert receipt is not None

    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", url,
        "--receipt-handle", receipt,
        "--visibility-timeout", "0",
    )
    assert result.returncode == 0

    got = None
    for _ in range(20):
        resp = sqs.rpc("ReceiveMessage", {
            "QueueUrl": url, "MaxNumberOfMessages": 1, "WaitTimeSeconds": 1,
        })
        msgs = resp.get("Messages") or []
        if msgs:
            got = msgs[0]
            break
    assert got is not None
    assert got["Body"] == body
