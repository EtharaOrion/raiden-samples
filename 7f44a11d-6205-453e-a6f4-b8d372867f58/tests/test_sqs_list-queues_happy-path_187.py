def test_list_queues_with_prefix_filter(cli, sqs):
    import json
    prefix = "listprefixtest-"
    match_name = prefix + "alpha"
    other_name = "otherqueue-beta"

    match_url = sqs.rpc("CreateQueue", {"QueueName": match_name})["QueueUrl"]
    other_url = sqs.rpc("CreateQueue", {"QueueName": other_name})["QueueUrl"]

    try:
        result = cli("sqs", "list-queues", "--queue-name-prefix", prefix)
        assert result.returncode == 0

        payload = json.loads(result.stdout)
        urls = payload.get("QueueUrls", [])
        assert any(u.endswith("/" + match_name) for u in urls)
        assert all(not u.endswith("/" + other_name) for u in urls)

        # Independent read via raw client
        listed = sqs.rpc("ListQueues", {"QueueNamePrefix": prefix}).get("QueueUrls", [])
        assert any(u.endswith("/" + match_name) for u in listed)
        assert all(not u.endswith("/" + other_name) for u in listed)
    finally:
        sqs.rpc("DeleteQueue", {"QueueUrl": match_url})
        sqs.rpc("DeleteQueue", {"QueueUrl": other_url})