def test_create_queue_rejects_invalid_attribute_definitions(cli, sqs, tmp_path):
    import hashlib

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:12]
    queue_name = f"invalid-args-{suffix}"

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith(f"/{queue_name}") for url in before.get("QueueUrls", [])
    )

    result = cli(
        "sqs",
        "create-queue",
        "--queue-name",
        queue_name,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith(f"/{queue_name}") for url in after.get("QueueUrls", [])
    )