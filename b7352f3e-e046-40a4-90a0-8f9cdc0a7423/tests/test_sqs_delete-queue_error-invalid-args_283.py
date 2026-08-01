def test_delete_queue_missing_queue_url_preserves_existing_queue(cli, sqs, tmp_path):
    import hashlib

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"delete-queue-invalid-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith("/" + queue_name)

    result = cli("sqs", "delete-queue")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    queue_urls = listed.get("QueueUrls", [])
    assert any(url.endswith("/" + queue_name) for url in queue_urls)