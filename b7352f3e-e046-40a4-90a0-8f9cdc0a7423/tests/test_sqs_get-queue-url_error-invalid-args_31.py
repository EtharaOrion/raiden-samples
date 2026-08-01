def test_get_queue_url_requires_queue_name(cli, sqs, tmp_path):
    import uuid

    queue_name = f"get-queue-url-required-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith(f"/{queue_name}")

    result = cli("sqs", "get-queue-url")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith(f"/{queue_name}") for url in listed.get("QueueUrls", [])
    )