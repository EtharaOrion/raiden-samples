def test_receive_message_round_trips_id_and_checksum(cli, sqs):
    import hashlib
    import json
    import uuid

    qname = "md5-recv-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    body = "roundtrip-payload-" + uuid.uuid4().hex
    sent = sqs.rpc("SendMessage", {"QueueUrl": url, "MessageBody": body})

    result = cli(
        "sqs", "receive-message",
        "--queue-url", url,
        "--max-number-of-messages", "1",
        "--wait-time-seconds", "5",
    )
    assert result.returncode == 0, result.stderr

    messages = json.loads(result.stdout)["Messages"]
    assert len(messages) == 1
    msg = messages[0]

    assert msg["Body"] == body
    assert msg["MessageId"] == sent["MessageId"]
    assert msg["MD5OfBody"] == sent["MD5OfMessageBody"]
    assert msg["MD5OfBody"] == hashlib.md5(body.encode()).hexdigest()
    assert msg["ReceiptHandle"]

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
