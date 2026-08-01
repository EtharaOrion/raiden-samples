def test_list_queues_with_prefix_filter(cli, sqs):
    import json
    prefix = "listqtest-"
    matching = prefix + "alpha"
    other = "nomatch-beta"

    sqs.rpc("CreateQueue", {"QueueName": matching})
    sqs.rpc("CreateQueue", {"QueueName": other})

    result = cli("sqs", "list-queues", "--queue-name-prefix", prefix)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    urls = out.get("QueueUrls", [])
    assert any(u.endswith("/" + matching) for u in urls)
    assert all(not u.endswith("/" + other) for u in urls)

    # Independent state read: the matching queue exists and prefix filter holds
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": prefix})
    state_urls = listed.get("QueueUrls", [])
    assert any(u.endswith("/" + matching) for u in state_urls)
    assert all(not u.endswith("/" + other) for u in state_urls)