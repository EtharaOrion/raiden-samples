def test_get_queue_attributes_happy_path(cli, sqs):
    queue_name = "test-get-attrs-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a message so ApproximateNumberOfMessages is meaningful
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in send

    result = cli(
        "sqs", "get-queue-attributes",
        "--queue-url", queue_url,
        "--attribute-names", "All",
    )
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    attrs = payload["Attributes"]
    assert isinstance(attrs, dict)
    assert "QueueArn" in attrs
    assert attrs["QueueArn"].endswith(queue_name)

    # Independent read-back via raw RPC
    got = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })
    assert got["Attributes"]["QueueArn"].endswith(queue_name)

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})