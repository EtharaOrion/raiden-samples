import json


import json
import time


def test_workflow_batch_send_receive_delete_visibility(cli, sqs, tmp_path):
    qname = "wf_batch_q"
    r = cli("sqs", "create-queue", "--queue-name", qname)
    assert r.returncode == 0
    qurl = json.loads(r.stdout)["QueueUrl"]
    assert qurl.endswith("/" + qname)

    entries = [
        {"Id": "a", "MessageBody": "body-a"},
        {"Id": "b", "MessageBody": "body-b"},
        {"Id": "c", "MessageBody": "body-c"},
    ]
    r = cli("sqs", "send-message-batch", "--queue-url", qurl, "--entries", json.dumps(entries))
    assert r.returncode == 0
    out = json.loads(r.stdout)
    succ_ids = {s["Id"] for s in out.get("Successful", [])}
    assert {"a", "b", "c"} <= succ_ids
    for s in out["Successful"]:
        assert s.get("MessageId")

    # count reflects batch send (prior send-message-batch effect)
    ok = False
    for _ in range(5):
        attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": qurl, "AttributeNames": ["All"]})["Attributes"]
        if int(attrs["ApproximateNumberOfMessages"]) >= 3:
            ok = True
            break
        time.sleep(1)
    assert ok

    # receive multiple messages, collect handles
    handles = []
    for _ in range(10):
        r = cli("sqs", "receive-message", "--queue-url", qurl)
        assert r.returncode == 0
        data = json.loads(r.stdout) if r.stdout.strip() else {}
        for m in data.get("Messages", []):
            handles.append(m["ReceiptHandle"])
        if len(handles) >= 3:
            break
        time.sleep(1)
    assert len(handles) >= 1

    # change visibility batch on received handles (prior receive effect)
    cmv_entries = [
        {"Id": str(i), "ReceiptHandle": h, "VisibilityTimeout": 30}
        for i, h in enumerate(handles)
    ]
    r = cli("sqs", "change-message-visibility-batch", "--queue-url", qurl,
            "--entries", json.dumps(cmv_entries))
    assert r.returncode == 0
    cmv_out = json.loads(r.stdout)
    cmv_ok = {s["Id"] for s in cmv_out.get("Successful", [])}
    assert cmv_ok == {str(i) for i in range(len(handles))}

    # reset visibility to 0 so we can delete now
    reset_entries = [
        {"Id": str(i), "ReceiptHandle": h, "VisibilityTimeout": 0}
        for i, h in enumerate(handles)
    ]
    r = cli("sqs", "change-message-visibility-batch", "--queue-url", qurl,
            "--entries", json.dumps(reset_entries))
    assert r.returncode == 0

    # delete the received messages via batch (prior receive handles)
    del_entries = [{"Id": str(i), "ReceiptHandle": h} for i, h in enumerate(handles)]
    r = cli("sqs", "delete-message-batch", "--queue-url", qurl, "--entries", json.dumps(del_entries))
    assert r.returncode == 0
    del_ok = {s["Id"] for s in json.loads(r.stdout).get("Successful", [])}
    assert del_ok == {str(i) for i in range(len(handles))}

    r = cli("sqs", "delete-queue", "--queue-url", qurl)
    assert r.returncode == 0
