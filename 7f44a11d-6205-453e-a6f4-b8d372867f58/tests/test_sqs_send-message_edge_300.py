def test_send_message_edge_delay_seconds_max(cli, sqs):
    import json
    import uuid

    qname = "edge-send-delay-max-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    body = "delay-max-body-" + uuid.uuid4().hex[:8]
    r = cli(
        "sqs", "send-message",
        "--queue-url", url,
        "--message-body", body,
        "--delay-seconds", "900",
    )
    assert r.returncode == 0
    sent = json.loads(r.stdout)
    assert sent.get("MessageId")

    # 15-minute delay: message is not immediately visible on short poll.
    resp = sqs.rpc("ReceiveMessage", {
        "QueueUrl": url,
        "MaxNumberOfMessages": 1,
        "WaitTimeSeconds": 0,
    })
    assert not (resp.get("Messages") or [])

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": url,
        "AttributeNames": ["All"],
    })["Attributes"]
    delayed = int(attrs.get("ApproximateNumberOfMessagesDelayed", "0"))
    visible = int(attrs.get("ApproximateNumberOfMessages", "0"))
    in_flight = int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert (delayed + visible + in_flight) >= 1

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
