def test_set_queue_attributes_missing_attributes_arg(cli, sqs):
    queue_name = "test-missing-attrs-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["VisibilityTimeout"],
    })["Attributes"]

    result = cli("sqs", "set-queue-attributes", "--queue-url", queue_url)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Attributes" in result.stderr or "argument" in result.stderr.lower()

    after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["VisibilityTimeout"],
    })["Attributes"]
    assert after["VisibilityTimeout"] == before["VisibilityTimeout"]

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})