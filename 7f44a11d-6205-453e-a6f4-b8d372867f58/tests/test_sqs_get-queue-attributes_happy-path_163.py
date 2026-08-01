def test_get_queue_attributes_happy_path(cli, sqs):
    queue_name = "test-gqa-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs", "get-queue-attributes",
        "--queue-url", queue_url,
        "--attribute-names", "All",
    )
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    attrs = payload["Attributes"]
    assert "ApproximateNumberOfMessages" in attrs

    # independent read of resulting state via raw client
    state = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })
    assert "ApproximateNumberOfMessages" in state["Attributes"]
    assert attrs["QueueArn"].endswith(queue_name)
    assert state["Attributes"]["QueueArn"].endswith(queue_name)