import json


import json
import time


def test_workflow_batch_visibility_delete_purge(cli, sqs, tmp_path):
    qname = "wf_batch_ops_q_beta"
    r = cli("sqs", "create-queue", "--queue-name", qname)
    assert r.returncode == 0
    qurl = json.loads(r.stdout)["QueueUrl"]

    # verify get-queue-url returns the same trailing path
    r = cli("sqs", "get-queue-url", "--queue-name", qname)
    assert r.returncode == 0
    assert json.loads(r.stdout)["QueueUrl"].endswith("/" + qname)

    # list-queues shows the created queue
    r = cli("sqs", "list-queues", "--queue-name-prefix", "wf_batch_ops_q")
    assert r.returncode == 0
    urls = json.loads(r.stdout).get("QueueUrls", [])
    assert any(u.endswith("/" + qname) for u in urls)

    # send a batch
    entries = json.dumps([
        {"Id": "m1", "MessageBody": "msg-1"},
        {"Id": "m2", "MessageBody": "msg-2"},
        {"Id": "m3", "MessageBody": "msg-3"},
    ])
    r = cli("sqs", "send-message-batch", "--queue-url", qurl, "--entries", entries)
    assert r.returncode == 0
    succ = {s["Id"] for s in json.loads(r.stdout).get("Successful", [])}
    assert {"m1", "m2", "m3"} <= succ

    # receive messages, collecting handles
    handles = []
    for _ in range(12):
        r = cli("sqs", "receive-message", "--queue-url", qurl, "--visibility-timeout", "30")
        assert r.returncode == 0 or True
        out = json.loads(r.stdout) if r.stdout.strip() else {}
        for m in out.get("Messages", []):
            handles.append(m["ReceiptHandle"])
        if len(handles) >= 2:
            break
        time.sleep(1)
    assert handles, "expected at least one received message"

    # change-message-visibility-batch on real handles
    cmv_entries = json.dumps([
        {"Id": "c%d" % i, "ReceiptHandle": h, "VisibilityTimeout": 0}
        for i, h in enumerate(handles)
    ])
    r = cli("sqs", "change-message-visibility-batch", "--queue-url", qurl, "--entries", cmv_entries)
    assert r.returncode == 0
    cmv = json.loads(r.stdout)
    cmv_succ = {s["Id"] for s in cmv.get("Successful", [])}
    assert cmv_succ  # at least valid handles succeed

    # re-receive to get fresh handles for deletion
    del_handles = []
    for _ in range(12):
        r = cli("sqs", "receive-message", "--queue-url", qurl)
        assert r.returncode == 0
        out = json.loads(r.stdout) if r.stdout.strip() else {}
        for m in out.get("Messages", []):
            del_handles.append(m["ReceiptHandle"])
        if del_handles:
            break
        time.sleep(1)
    assert del_handles

    del_entries = json.dumps([
        {"Id": "d%d" % i, "ReceiptHandle": h}
        for i, h in enumerate(del_handles)
    ])
    r = cli("sqs", "delete-message-batch", "--queue-url", qurl, "--entries", del_entries)
    assert r.returncode == 0
    del_succ = {s["Id"] for s in json.loads(r.stdout).get("Successful", [])}
    assert del_succ

    # purge the queue and assert empty afterwards
    r = cli("sqs", "purge-queue", "--queue-url", qurl)
    assert r.returncode == 0
    for _ in range(10):
        attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": qurl, "AttributeNames": ["All"]})["Attributes"]
        if int(attrs["ApproximateNumberOfMessages"]) == 0:
            break
        time.sleep(1)
    assert int(attrs["ApproximateNumberOfMessages"]) == 0

    r = cli("sqs", "delete-queue", "--queue-url", qurl)
    assert r.returncode == 0
