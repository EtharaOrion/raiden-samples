def test_get_queue_attributes_happy_path(cli, sqs):
    queue_name = "test-gqa-happy-queue"
    created = sqs.rpc("CreateQueue", {
        "QueueName": queue_name,
        "Attributes": {"VisibilityTimeout": "45"},
    })
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
    assert attrs["VisibilityTimeout"] == "45"

    state = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })
    assert state["Attributes"]["VisibilityTimeout"] == "45"