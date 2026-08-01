def test_purge_queue_invalid_args(cli, sqs, tmp_path):
    queue_name = "test-purge-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a message so we can prove purge did NOT happen
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})

    result = cli(
        "sqs", "purge-queue",
        "--queue-url", queue_url,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "argument" in result.stderr.lower() or "Unknown" in result.stderr or "unrecognized" in result.stderr.lower()

    # State unchanged: message still present (purge did not run)
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) >= 1