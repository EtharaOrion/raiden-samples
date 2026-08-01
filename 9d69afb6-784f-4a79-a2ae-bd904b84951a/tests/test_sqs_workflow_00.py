import json


import json
import time


def test_workflow_create_send_receive_delete_purge(cli, sqs, tmp_path):
    qname = "wf_send_recv_q"
    r = cli("sqs", "create-queue", "--queue-name", qname)
    assert r.returncode == 0
    qurl = json.loads(r.stdout)["QueueUrl"]
    assert qurl.endswith("/" + qname)

    # verify via get-queue-url that the queue exists (prior create effect)
    r = cli("sqs", "get-queue-url", "--queue-name", qname)
    assert r.returncode == 0
    assert json.loads(r.stdout)["QueueUrl"].endswith("/" + qname)

    # list-queues should include our queue name
    r = cli("sqs", "list-queues", "--queue-name-prefix", qname)
    assert r.returncode == 0
    urls = json.loads(r.stdout).get("QueueUrls", [])
    assert any(u.endswith("/" + qname) for u in urls)

    # send a message
    r = cli("sqs", "send-message", "--queue-url", qurl, "--message-body", "hello-world")
    assert r.returncode == 0
    assert "MessageId" in json.loads(r.stdout)

    # assert queue count reflects the send (prior send effect)
    attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": qurl, "AttributeNames": ["All"]})["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) >= 1

    # receive the message, capture receipt handle
    handle = None
    body = None
    for _ in range(5):
        r = cli("sqs", "receive-message", "--queue-url", qurl)
        assert r.returncode == 0
        out = json.loads(r.stdout) if r.stdout.strip() else {}
        msgs = out.get("Messages", [])
        if msgs:
            handle = msgs[0]["ReceiptHandle"]
            body = msgs[0]["Body"]
            break
        time.sleep(1)
    assert handle is not None
    assert body == "hello-world"

    # change visibility on the received handle
    r = cli("sqs", "change-message-visibility", "--queue-url", qurl,
            "--receipt-handle", handle, "--visibility-timeout", "0")
    assert r.returncode == 0

    # delete the message using the handle from the earlier receive
    r = cli("sqs", "delete-message", "--queue-url", qurl, "--receipt-handle", handle)
    assert r.returncode == 0

    # send more, then purge
    r = cli("sqs", "send-message", "--queue-url", qurl, "--message-body", "to-purge")
    assert r.returncode == 0
    r = cli("sqs", "purge-queue", "--queue-url", qurl)
    assert r.returncode == 0

    # after purge, count should eventually be 0 (prior purge effect)
    ok = False
    for _ in range(5):
        attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": qurl, "AttributeNames": ["All"]})["Attributes"]
        if int(attrs["ApproximateNumberOfMessages"]) == 0:
            ok = True
            break
        time.sleep(1)
    assert ok

    # cleanup
    r = cli("sqs", "delete-queue", "--queue-url", qurl)
    assert r.returncode == 0
