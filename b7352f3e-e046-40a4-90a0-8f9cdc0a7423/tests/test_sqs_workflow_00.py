import json


import json
import time


def test_workflow_create_send_receive_delete_visibility(cli, sqs, tmp_path):
    qname = "wf_send_recv_q_alpha"
    r = cli("sqs", "create-queue", "--queue-name", qname)
    assert r.returncode == 0
    qurl = json.loads(r.stdout)["QueueUrl"]
    assert qurl.endswith("/" + qname)

    # send a single message
    r = cli("sqs", "send-message", "--queue-url", qurl, "--message-body", "hello-world")
    assert r.returncode == 0
    sent = json.loads(r.stdout)
    assert sent.get("MessageId")

    # send a batch
    entries = json.dumps([
        {"Id": "b1", "MessageBody": "batch-one"},
        {"Id": "b2", "MessageBody": "batch-two"},
    ])
    r = cli("sqs", "send-message-batch", "--queue-url", qurl, "--entries", entries)
    assert r.returncode == 0
    batch = json.loads(r.stdout)
    succ_ids = {s["Id"] for s in batch.get("Successful", [])}
    assert {"b1", "b2"} <= succ_ids
    for s in batch.get("Successful", []):
        assert s.get("MessageId")

    # confirm count grew via prior sends
    attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": qurl, "AttributeNames": ["All"]})["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) >= 1

    # receive some messages (tolerate eventual consistency)
    received = []
    for _ in range(10):
        r = cli("sqs", "receive-message", "--queue-url", qurl)
        assert r.returncode == 0
        out = json.loads(r.stdout) if r.stdout.strip() else {}
        for m in out.get("Messages", []):
            received.append(m)
        if received:
            break
        time.sleep(1)
    assert received, "expected at least one message from prior sends"

    handle = received[0]["ReceiptHandle"]

    # change visibility on a real handle
    r = cli("sqs", "change-message-visibility", "--queue-url", qurl,
            "--receipt-handle", handle, "--visibility-timeout", "0")
    assert r.returncode == 0

    # delete the received message
    r = cli("sqs", "delete-message", "--queue-url", qurl, "--receipt-handle", handle)
    assert r.returncode == 0

    # cleanup
    r = cli("sqs", "delete-queue", "--queue-url", qurl)
    assert r.returncode == 0
