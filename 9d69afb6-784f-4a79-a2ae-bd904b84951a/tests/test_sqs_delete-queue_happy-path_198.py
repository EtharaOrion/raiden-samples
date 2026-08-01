def test_delete_queue_happy_path(cli, sqs):
    queue_name = "test-delete-queue-happy"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Confirm it exists before deletion
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    # Assert the queue no longer resolves
    try:
        after = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
        # If it still returns a URL, the delete did not take effect
        assert not after.get("QueueUrl", "").endswith("/" + queue_name)
    except Exception:
        # NonExistentQueue error is the expected outcome
        pass

    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(u.endswith("/" + queue_name) for u in listed_after.get("QueueUrls", []))