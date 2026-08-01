def test_list_queues_happy_path(cli, sqs):
    import json, uuid

    queue_name = "test-list-queues-" + uuid.uuid4().hex[:12]
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli("sqs", "list-queues")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    urls = payload.get("QueueUrls", [])
    assert any(u.endswith("/" + queue_name) for u in urls)

    listed = sqs.rpc("ListQueues", {})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))