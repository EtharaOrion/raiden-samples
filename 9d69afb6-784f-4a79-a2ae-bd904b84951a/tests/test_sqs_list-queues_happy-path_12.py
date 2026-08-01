def test_list_queues_happy_path(cli, sqs):
    import json, uuid

    qname = "list-queues-test-" + uuid.uuid4().hex[:8]
    created = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    result = cli("sqs", "list-queues")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    urls = payload.get("QueueUrls", [])
    assert any(u.endswith("/" + qname) for u in urls)

    listed = sqs.rpc("ListQueues", {})
    assert any(u.endswith("/" + qname) for u in listed.get("QueueUrls", []))

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})