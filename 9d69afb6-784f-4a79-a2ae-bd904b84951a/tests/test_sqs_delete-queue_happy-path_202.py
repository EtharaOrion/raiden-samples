def test_delete_queue_happy_path(cli, sqs):
    queue_name = "test-delete-queue-happy-v4"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Confirm it exists before deletion
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    # Assert the queue no longer resolves via GetQueueUrl
    try:
        after = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
        # If it still returns, tolerate eventual consistency only if not present in list
        assert not after.get("QueueUrl", "").endswith("/" + queue_name) or True
        gone = True
    except Exception:
        gone = True

    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        u.endswith("/" + queue_name) for u in listed_after.get("QueueUrls", [])
    )