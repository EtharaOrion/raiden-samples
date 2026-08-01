def test_send_message_edge_large_body(cli, sqs):
    import json
    import uuid

    qname = "edge-send-large-body-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    body = "B" * 100_000
    r = cli(
        "sqs", "send-message",
        "--queue-url", url,
        "--message-body", body,
    )
    assert r.returncode == 0
    sent = json.loads(r.stdout)
    assert sent.get("MessageId")

    resp = sqs.rpc("ReceiveMessage", {
        "QueueUrl": url,
        "MaxNumberOfMessages": 1,
        "WaitTimeSeconds": 5,
    })
    msgs = resp.get("Messages") or []
    assert len(msgs) == 1
    assert msgs[0]["Body"] == body
    assert len(msgs[0]["Body"]) == 100_000

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
