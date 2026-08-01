def test_get_queue_attributes_happy_path(cli, sqs, tmp_path):
    import json
    import uuid

    queue_name = f"get-attributes-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "47"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs",
        "get-queue-attributes",
        "--queue-url",
        queue_url,
    )

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    assert isinstance(output, dict)

    observed = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["All"],
        },
    )
    assert observed["Attributes"]["VisibilityTimeout"] == "47"