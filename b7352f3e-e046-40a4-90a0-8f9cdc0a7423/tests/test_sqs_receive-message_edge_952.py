def test_receive_message_all_attributes_populated(cli, sqs):
    import json
    import uuid

    qname = "recv-attrs-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]
    sqs.rpc("SendMessage", {"QueueUrl": url, "MessageBody": "attr-payload"})

    result = cli(
        "sqs", "receive-message",
        "--queue-url", url,
        "--max-number-of-messages", "1",
        "--wait-time-seconds", "5",
        "--attribute-names", "All",
    )
    assert result.returncode == 0, result.stderr

    messages = json.loads(result.stdout)["Messages"]
    assert len(messages) == 1
    attrs = messages[0]["Attributes"]

    assert attrs["ApproximateReceiveCount"] == "1"
    assert attrs["SenderId"]
    for key in ("SentTimestamp", "ApproximateFirstReceiveTimestamp"):
        assert attrs[key].isdigit(), (key, attrs[key])

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
