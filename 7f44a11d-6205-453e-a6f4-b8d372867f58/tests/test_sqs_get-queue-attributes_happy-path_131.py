def test_get_queue_attributes_happy_path(cli, sqs):
    queue_name = "test_gqa_happy_v6"
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

    # Independent read-back of the resulting/known state via sqs
    state = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })
    assert "QueueArn" in state["Attributes"]
    assert state["Attributes"]["QueueArn"].endswith(queue_name)

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})