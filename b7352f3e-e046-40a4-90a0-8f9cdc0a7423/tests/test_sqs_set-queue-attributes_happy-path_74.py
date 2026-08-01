def test_set_queue_attributes_updates_visibility_timeout(cli, sqs, tmp_path):
    import json

    queue_name = f"set-attributes-{tmp_path.name}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "31"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert before["Attributes"]["VisibilityTimeout"] == "31"

    result = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        queue_url,
        "--attributes",
        json.dumps({"VisibilityTimeout": "47"}),
    )
    assert result.returncode == 0

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert after["Attributes"]["VisibilityTimeout"] == "47"