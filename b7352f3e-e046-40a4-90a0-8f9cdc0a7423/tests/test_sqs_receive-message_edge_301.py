import json
import time
import uuid


def test_receive_message_edge_max_number_of_messages_ten(cli, sqs):
    qname = "edge-recv-max10-" + uuid.uuid4().hex[:16]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    bodies = [f"m-{i}-" + uuid.uuid4().hex[:8] for i in range(10)]
    for b in bodies:
        sqs.rpc("SendMessage", {"QueueUrl": url, "MessageBody": b})

    deadline = time.time() + 5.0
    while time.time() < deadline:
        attrs = sqs.rpc("GetQueueAttributes", {
            "QueueUrl": url, "AttributeNames": ["ApproximateNumberOfMessages"],
        })["Attributes"]
        if int(attrs["ApproximateNumberOfMessages"]) >= 10:
            break
        time.sleep(0.1)

    result = cli(
        "sqs", "receive-message",
        "--queue-url", url,
        "--max-number-of-messages", "10",
        "--wait-time-seconds", "5",
    )
    assert result.returncode == 0

    parsed = json.loads(result.stdout) if result.stdout.strip() else {}
    msgs = parsed.get("Messages") or []
    assert 1 <= len(msgs) <= 10
    sent_set = set(bodies)
    for m in msgs:
        assert m["Body"] in sent_set
        assert m.get("ReceiptHandle")
