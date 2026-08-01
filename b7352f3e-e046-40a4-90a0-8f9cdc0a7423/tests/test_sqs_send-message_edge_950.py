def test_send_message_returns_body_checksum(cli, sqs):
    import hashlib
    import json
    import uuid

    qname = "md5-send-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    body = "checksum-payload-" + uuid.uuid4().hex
    result = cli("sqs", "send-message", "--queue-url", url, "--message-body", body)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["MD5OfMessageBody"] == hashlib.md5(body.encode()).hexdigest()
    assert out["MessageId"]
    assert set(out) == {"MD5OfMessageBody", "MessageId"}

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
