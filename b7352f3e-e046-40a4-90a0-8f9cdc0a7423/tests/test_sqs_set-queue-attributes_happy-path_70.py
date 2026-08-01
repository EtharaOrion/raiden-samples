def test_set_queue_attributes_updates_visibility_timeout(cli, sqs):
    import json
    import time
    import uuid

    queue_name = f"set-attributes-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

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

    deadline = time.monotonic() + 65
    while True:
        after = sqs.rpc(
            "GetQueueAttributes",
            {
                "QueueUrl": queue_url,
                "AttributeNames": ["VisibilityTimeout"],
            },
        )
        if after["Attributes"].get("VisibilityTimeout") == "45":
            break
        if time.monotonic() >= deadline:
            assert after["Attributes"].get("VisibilityTimeout") == "45"
        time.sleep(1)