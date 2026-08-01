def test_set_queue_attributes_rejects_invalid_attribute_name(cli, sqs):
    import json
    import uuid

    queue_name = f"set-attributes-invalid-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "47"},
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
    assert before["Attributes"]["VisibilityTimeout"] == "47"

    result = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        queue_url,
        "--attributes",
        json.dumps({"DefinitelyInvalidAttribute": "value"}),
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidAttributeName" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert after["Attributes"]["VisibilityTimeout"] == "47"