def test_get_queue_attributes_invalid_arg(cli, sqs):
    queue_name = "test-invalid-arg-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs", "get-queue-attributes",
        "--queue-url", queue_url,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "rgument" in result.stderr or "Unknown" in result.stderr or "usage" in result.stderr.lower()

    # Queue itself is unaffected and still readable
    attrs = sqs.rpc("GetQueueAttributes", {"QueueUrl": queue_url, "AttributeNames": ["All"]})
    assert "Attributes" in attrs