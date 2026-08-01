def test_create_queue_invalid_args(cli, sqs):
    queue_name = "test-invalid-flag-queue"
    result = cli("sqs", "create-queue", "--queue-name", queue_name,
                 "--not-a-real-flag", "x")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls") or []
    assert not any(u.endswith("/" + queue_name) for u in urls)