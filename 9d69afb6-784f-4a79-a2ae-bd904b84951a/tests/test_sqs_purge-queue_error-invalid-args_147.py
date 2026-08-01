def test_purge_queue_invalid_flag_rejected(cli, sqs):
    queue_name = "test-purge-invalid-flag-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    # Seed a message so we can prove purge did NOT run.
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})

    result = cli(
        "sqs", "purge-queue",
        "--queue-url", queue_url,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown" in result.stderr or "unrecognized" in result.stderr.lower()

    # State assertion: message still present since purge was rejected.
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert int(attrs["Attributes"]["ApproximateNumberOfMessages"]) >= 1