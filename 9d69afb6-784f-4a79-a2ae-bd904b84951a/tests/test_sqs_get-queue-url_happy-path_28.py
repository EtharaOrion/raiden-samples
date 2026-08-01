def test_get_queue_url_happy_path(cli, sqs):
    queue_name = "test_get_queue_url_happy"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    expected_url = created["QueueUrl"]
    assert expected_url.endswith("/" + queue_name)

    result = cli("sqs", "get-queue-url", "--queue-name", queue_name)
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    returned_url = payload["QueueUrl"]
    assert returned_url.endswith("/" + queue_name)

    # Independent read-back: the returned URL must reference the real queue
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls", [])
    assert any(u.endswith("/" + queue_name) for u in urls)

    # The CLI-returned URL must be usable for further operations
    attrs = sqs.rpc("GetQueueAttributes",
                    {"QueueUrl": returned_url, "AttributeNames": ["All"]})
    assert "Attributes" in attrs