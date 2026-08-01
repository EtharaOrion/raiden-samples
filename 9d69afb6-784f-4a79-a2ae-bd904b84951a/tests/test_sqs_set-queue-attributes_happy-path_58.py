def test_set_queue_attributes_happy_path(cli, sqs):
    queue_name = "test-set-attrs-queue-v4"
    create = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = create["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["VisibilityTimeout"],
    })
    assert before["Attributes"].get("VisibilityTimeout") != "45"

    result = cli(
        "sqs", "set-queue-attributes",
        "--queue-url", queue_url,
        "--attributes", '{"VisibilityTimeout":"45"}',
    )
    assert result.returncode == 0

    after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["VisibilityTimeout"],
    })
    assert after["Attributes"].get("VisibilityTimeout") == "45"