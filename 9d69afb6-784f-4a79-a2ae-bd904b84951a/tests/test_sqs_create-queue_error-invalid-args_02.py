def test_create_queue_invalid_flag_rejected(cli, sqs):
    queue_name = "test-invalid-flag-queue-xyz"
    result = cli("sqs", "create-queue", "--queue-name", queue_name,
                 "--not-a-real-flag", "x")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "Invalid" in result.stderr \
        or "usage" in result.stderr.lower()
    # Assert the queue was NOT created as a side effect of the bad invocation.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in urls)