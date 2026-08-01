import json


import json


def test_workflow_create_send_receive_delete(cli, sqs, tmp_path):
    qname = "wf-create-send-receive-delete-q1"
    r = cli("sqs", "create-queue", "--queue-name", qname)
    assert r.returncode == 0
    qurl = json.loads(r.stdout)["QueueUrl"]
    assert qurl.endswith("/" + qname)

    # verify via list-queues (prior create effect)
    r = cli("sqs", "list-queues", "--queue-name-prefix", qname)
    assert r.returncode == 0
    urls = json.loads(r.stdout).get("QueueUrls", [])
    assert any(u.endswith("/" + qname) for u in urls)

    body = "hello-workflow-body"
    r = cli("sqs", "send-message", "--queue-url", qurl, "--message-body", body)
    assert r.returncode == 0
    sent = json.loads(r.stdout)
    assert sent.get("MessageId")

    # confirm the send effect via backend attributes
    attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": qurl, "AttributeNames": ["All"]})["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) >= 1

    # receive (may be empty on first read); retry to obtain a receipt handle
    handle = None
    for _ in range(5):
        r = cli("sqs", "receive-message", "--queue-url", qurl)
        assert r.returncode == 0
        msgs = json.loads(r.stdout).get("Messages", [])
        if msgs:
            assert msgs[0]["Body"] == body
            handle = msgs[0]["ReceiptHandle"]
            break
    assert handle is not None

    r = cli("sqs", "delete-message", "--queue-url", qurl, "--receipt-handle", handle)
    assert r.returncode == 0

    # cleanup
    r = cli("sqs", "delete-queue", "--queue-url", qurl)
    assert r.returncode == 0
