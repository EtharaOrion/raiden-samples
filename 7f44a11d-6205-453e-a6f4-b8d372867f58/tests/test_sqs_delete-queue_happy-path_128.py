def test_delete_queue_removes_existing_queue(cli, sqs):
    queue_name = "test-delete-queue-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(u.endswith("/" + queue_name) for u in after.get("QueueUrls", []))