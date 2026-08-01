def test_delete_queue_happy_path(cli, sqs):
    queue_name = "test-delete-queue-happy"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # confirm it exists before deletion
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    # verify the queue is gone
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(u.endswith("/" + queue_name) for u in after.get("QueueUrls", []))