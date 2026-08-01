def test_create_queue_missing_required_queue_name(cli, sqs):
    before = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []

    result = cli("sqs", "create-queue")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "queue-name" in result.stderr.lower() or "required" in result.stderr.lower()

    after = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert set(after) == set(before)