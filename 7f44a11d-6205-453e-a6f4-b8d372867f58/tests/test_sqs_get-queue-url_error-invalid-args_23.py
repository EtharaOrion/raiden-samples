def test_get_queue_url_invalid_flag_rejected(cli, sqs):
    queue_name = "test-invalid-flag-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs", "get-queue-url",
        "--queue-name", queue_name,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    # Assert the queue still exists and is retrievable (state unaffected)
    got = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert got["QueueUrl"].endswith("/" + queue_name)