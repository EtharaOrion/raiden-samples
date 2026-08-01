def test_create_queue_edge_name_at_max_length(cli, sqs):
    import json
    import uuid

    # SQS caps queue names at 80 characters; test exactly at the limit.
    suffix = uuid.uuid4().hex[:12]
    qname = ("qmax-" + suffix + "-" + "a" * 80)[:80]
    assert len(qname) == 80

    r = cli("sqs", "create-queue", "--queue-name", qname)
    assert r.returncode == 0
    parsed = json.loads(r.stdout)
    assert parsed.get("QueueUrl")
    assert parsed["QueueUrl"].endswith("/" + qname)

    got = sqs.rpc("GetQueueUrl", {"QueueName": qname})
    assert got["QueueUrl"].endswith("/" + qname)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": qname[:20]})
    assert any(u.endswith("/" + qname) for u in listed.get("QueueUrls", []))

    sqs.rpc("DeleteQueue", {"QueueUrl": parsed["QueueUrl"]})
