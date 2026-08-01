def test_list_queues_happy_path(cli, sqs):
    import json
    queue_name = "test-list-queues-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli("sqs", "list-queues")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    urls = payload.get("QueueUrls", [])
    assert any(u.endswith("/" + queue_name) for u in urls)

    listing = sqs.rpc("ListQueues", {})
    assert any(u.endswith("/" + queue_name) for u in listing.get("QueueUrls", []))