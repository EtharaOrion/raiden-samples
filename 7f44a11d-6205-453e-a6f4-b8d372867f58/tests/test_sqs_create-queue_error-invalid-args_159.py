def test_create_queue_name_too_long_rejected(cli, sqs):
    long_name = "x" * 300
    result = cli("sqs", "create-queue", "--queue-name", long_name)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "InvalidParameter" in result.stderr or "Invalid" in result.stderr
    # Assert the queue was NOT created
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": long_name})
    urls = listed.get("QueueUrls", []) or []
    assert not any(u.endswith("/" + long_name) for u in urls)