def test_get_queue_attributes_happy_path(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"get-attributes-{suffix}"

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
    assert result.returncode == 0

    if result.stdout.strip():
        output = json.loads(result.stdout)
        assert isinstance(output, dict)
        if "Attributes" in output:
            assert isinstance(output["Attributes"], dict)

    state = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert state["Attributes"]["VisibilityTimeout"] == "47"