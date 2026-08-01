def test_list_queues_with_prefix_and_max_results(cli, sqs):
    import json
    prefix = "listtest-prefix-"
    q1 = prefix + "alpha"
    q2 = prefix + "beta"
    other = "unrelated-queue-name"

    url1 = sqs.rpc("CreateQueue", {"QueueName": q1})["QueueUrl"]
    url2 = sqs.rpc("CreateQueue", {"QueueName": q2})["QueueUrl"]
    sqs.rpc("CreateQueue", {"QueueName": other})

    result = cli("sqs", "list-queues", "--queue-name-prefix", prefix,
                 "--max-results", "10")
    assert result.returncode == 0

    payload = json.loads(result.stdout)
    urls = payload.get("QueueUrls", [])
    assert isinstance(urls, list)

    # every returned url must begin with the prefix (end with a name that starts with prefix)
    for u in urls:
        name = u.rsplit("/", 1)[-1]
        assert name.startswith(prefix)

    returned_names = {u.rsplit("/", 1)[-1] for u in urls}
    assert q1 in returned_names
    assert q2 in returned_names
    assert other not in returned_names

    # independent state read confirms the prefix filtering
    state = sqs.rpc("ListQueues", {"QueueNamePrefix": prefix})
    state_names = {u.rsplit("/", 1)[-1] for u in state.get("QueueUrls", [])}
    assert q1 in state_names
    assert q2 in state_names

    sqs.rpc("DeleteQueue", {"QueueUrl": url1})
    sqs.rpc("DeleteQueue", {"QueueUrl": url2})