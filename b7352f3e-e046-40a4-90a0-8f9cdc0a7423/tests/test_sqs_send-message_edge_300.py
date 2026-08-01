import uuid


def test_send_message_edge_delay_seconds_max_boundary(cli, sqs):
    qname = "edge-send-delay900-" + uuid.uuid4().hex[:16]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    body = "delay-max-" + uuid.uuid4().hex
    result = cli(
        "sqs", "send-message",
        "--queue-url", url,
        "--message-body", body,
        "--delay-seconds", "900",
    )
    assert result.returncode == 0

    resp = sqs.rpc("ReceiveMessage", {
        "QueueUrl": url, "MaxNumberOfMessages": 1, "WaitTimeSeconds": 0,
    })
    assert not (resp.get("Messages") or [])

    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": url, "AttributeNames": ["All"],
    })["Attributes"]
    visible = int(attrs.get("ApproximateNumberOfMessages", "0"))
    delayed = int(attrs.get("ApproximateNumberOfMessagesDelayed", "0"))
    in_flight = int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0"))
    assert visible + delayed + in_flight >= 1
