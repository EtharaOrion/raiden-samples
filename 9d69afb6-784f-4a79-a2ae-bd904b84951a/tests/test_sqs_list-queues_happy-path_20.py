def test_list_queues_with_prefix_filter(cli, sqs):
    import json, uuid

    prefix = "listtest-" + uuid.uuid4().hex[:8]
    matching = prefix + "-alpha"
    other = "other-" + uuid.uuid4().hex[:8]

    match_url = sqs.rpc("CreateQueue", {"QueueName": matching})["QueueUrl"]
    other_url = sqs.rpc("CreateQueue", {"QueueName": other})["QueueUrl"]

    try:
        result = cli("sqs", "list-queues", "--queue-name-prefix", prefix)
        assert result.returncode == 0

        payload = json.loads(result.stdout)
        urls = payload.get("QueueUrls", [])

        assert any(u.endswith("/" + matching) for u in urls)
        assert all(not u.endswith("/" + other) for u in urls)

        # independent read-back via raw sqs
        state = sqs.rpc("ListQueues", {"QueueNamePrefix": prefix}).get("QueueUrls", [])
        assert any(u.endswith("/" + matching) for u in state)
        assert all(not u.endswith("/" + other) for u in state)
    finally:
        sqs.rpc("DeleteQueue", {"QueueUrl": match_url})
        sqs.rpc("DeleteQueue", {"QueueUrl": other_url})