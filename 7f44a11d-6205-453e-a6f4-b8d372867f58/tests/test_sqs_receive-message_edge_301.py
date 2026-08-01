def test_receive_message_edge_max_number_one(cli, sqs):
    import json
    import uuid

    qname = "edge-recv-max-one-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    for i in range(3):
        sqs.rpc("SendMessage", {"QueueUrl": url, "MessageBody": f"only-one-{i}"})

    r = cli(
        "sqs", "receive-message",
        "--queue-url", url,
        "--max-number-of-messages", "1",
        "--wait-time-seconds", "3",
    )
    assert r.returncode == 0

    parsed = json.loads(r.stdout) if r.stdout.strip() else {}
    msgs = parsed.get("Messages") or []
    # MaxNumberOfMessages=1 caps this receive at exactly one message.
    assert len(msgs) == 1
    assert msgs[0].get("MessageId")
    assert msgs[0].get("ReceiptHandle")
    assert msgs[0].get("Body", "").startswith("only-one-")

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
