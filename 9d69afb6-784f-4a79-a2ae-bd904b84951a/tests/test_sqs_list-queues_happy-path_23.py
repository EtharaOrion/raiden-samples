def test_list_queues_with_prefix(cli, sqs):
    import json, uuid

    prefix = "listqtest-" + uuid.uuid4().hex[:8]
    match_name = prefix + "-match"
    other_name = "other-" + uuid.uuid4().hex[:8]

    match_url = sqs.rpc("CreateQueue", {"QueueName": match_name})["QueueUrl"]
    other_url = sqs.rpc("CreateQueue", {"QueueName": other_name})["QueueUrl"]

    try:
        result = cli("sqs", "list-queues", "--queue-name-prefix", prefix)
        assert result.returncode == 0, result.stderr

        out = json.loads(result.stdout) if result.stdout.strip() else {}
        urls = out.get("QueueUrls", [])
        assert any(u.endswith("/" + match_name) for u in urls), urls
        assert not any(u.endswith("/" + other_name) for u in urls), urls

        # Independent state read confirms the match queue exists under the prefix.
        listed = sqs.rpc("ListQueues", {"QueueNamePrefix": prefix}).get("QueueUrls", [])
        assert any(u.endswith("/" + match_name) for u in listed), listed
    finally:
        sqs.rpc("DeleteQueue", {"QueueUrl": match_url})
        sqs.rpc("DeleteQueue", {"QueueUrl": other_url})