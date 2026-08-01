def test_delete_queue_nonexistent(cli, sqs, tmp_path):
    import uuid

    token = uuid.uuid4().hex
    sentinel_name = f"delete-sentinel-{token}"
    missing_name = f"delete-missing-{token}"

    created = sqs.rpc("CreateQueue", {"QueueName": sentinel_name})
    sentinel_url = created["QueueUrl"]
    missing_url = f"{sentinel_url.rsplit('/', 1)[0]}/{missing_name}"

    before = sqs.rpc("ListQueues", {})
    before_urls = before.get("QueueUrls", [])
    assert any(url.endswith(f"/{sentinel_name}") for url in before_urls)
    assert not any(url.endswith(f"/{missing_name}") for url in before_urls)

    result = cli("sqs", "delete-queue", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    after = sqs.rpc("ListQueues", {})
    after_urls = after.get("QueueUrls", [])
    assert any(url.endswith(f"/{sentinel_name}") for url in after_urls)
    assert not any(url.endswith(f"/{missing_name}") for url in after_urls)