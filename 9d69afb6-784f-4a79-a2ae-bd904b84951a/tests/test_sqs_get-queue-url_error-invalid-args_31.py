def test_get_queue_url_invalid_args(cli, sqs, tmp_path):
    queue_name = "test-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith("/" + queue_name)

    result = cli(
        "sqs", "get-queue-url",
        "--queue-name", queue_name,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "argument" in result.stderr.lower() or "Exception" in result.stderr or "unknown" in result.stderr.lower()

    # Queue still exists and is retrievable
    got = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert got["QueueUrl"].endswith("/" + queue_name)