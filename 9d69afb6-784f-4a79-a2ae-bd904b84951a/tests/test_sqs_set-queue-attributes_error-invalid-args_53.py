def test_set_queue_attributes_invalid_flag(cli, sqs):
    queue_name = "test-invalid-flag-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["VisibilityTimeout"],
    })
    before_val = before["Attributes"]["VisibilityTimeout"]

    result = cli(
        "sqs", "set-queue-attributes",
        "--queue-url", queue_url,
        "--attributes", '{"VisibilityTimeout":"45"}',
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["VisibilityTimeout"],
    })
    assert after["Attributes"]["VisibilityTimeout"] == before_val