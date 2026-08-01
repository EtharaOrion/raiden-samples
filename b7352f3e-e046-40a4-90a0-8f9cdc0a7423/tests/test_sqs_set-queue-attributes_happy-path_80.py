def test_set_queue_attributes_updates_visibility_timeout(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:12]
    queue_name = f"set-attributes-{suffix}"

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
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
    assert before["Attributes"]["VisibilityTimeout"] == "30"

    result = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        queue_url,
        "--attributes",
        json.dumps({"VisibilityTimeout": "45"}),
    )
    assert result.returncode == 0

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert after["Attributes"]["VisibilityTimeout"] == "45"