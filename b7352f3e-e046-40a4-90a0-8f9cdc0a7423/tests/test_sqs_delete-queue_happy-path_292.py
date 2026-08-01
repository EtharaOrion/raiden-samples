def test_delete_queue_removes_existing_queue(cli, sqs, tmp_path):
    queue_name = f"delete-queue-{abs(hash(str(tmp_path)))}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "message deleted with queue"},
    )
    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith(f"/{queue_name}") for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)

    assert result.returncode == 0
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith(f"/{queue_name}") for url in after.get("QueueUrls", [])
    )