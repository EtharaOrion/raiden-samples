def test_delete_queue_happy_path(cli, sqs):
    queue_name = "test-delete-queue-happy"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    urls_before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(u.endswith("/" + queue_name) for u in urls_before)

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    urls_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert not any(u.endswith("/" + queue_name) for u in urls_after)