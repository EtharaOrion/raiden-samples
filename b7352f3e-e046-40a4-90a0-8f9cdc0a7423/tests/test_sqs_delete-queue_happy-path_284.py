def test_delete_queue_removes_existing_queue(cli, sqs):
    import uuid

    queue_name = f"delete-happy-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": "message deleted with queue",
        },
    )

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith(f"/{queue_name}") for url in listed.get("QueueUrls", [])
    )