def test_get_queue_url_rejects_unknown_flag(cli, sqs, tmp_path):
    import uuid

    queue_name = f"invalid-args-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    result = cli(
        "sqs",
        "get-queue-url",
        "--queue-name",
        queue_name,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith(f"/{queue_name}") for url in queues)