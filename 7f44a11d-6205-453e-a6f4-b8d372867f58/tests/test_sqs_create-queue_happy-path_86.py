def test_create_queue_happy_path(cli, sqs):
    queue_name = "test_string_v6_queue"

    # Ensure clean slate: remove if it exists
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    for url in existing.get("QueueUrls", []) or []:
        if url.rstrip("/").endswith("/" + queue_name):
            sqs.rpc("DeleteQueue", {"QueueUrl": url})

    # Run command under test
    result = cli("sqs", "create-queue", "--queue-name", queue_name)
    assert result.returncode == 0

    # Assert resulting state via independent read
    got = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    queue_url = got["QueueUrl"]
    assert queue_url.rstrip("/").endswith("/" + queue_name)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls", []) or []
    assert any(u.rstrip("/").endswith("/" + queue_name) for u in urls)

    # Cleanup
    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})