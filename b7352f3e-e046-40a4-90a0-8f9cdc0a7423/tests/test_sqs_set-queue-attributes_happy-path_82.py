def test_set_queue_attributes_updates_visibility_timeout(cli, sqs, tmp_path):
    import time

    queue_name = "set-attributes-" + tmp_path.name
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "31"},
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
    assert before["Attributes"]["VisibilityTimeout"] == "31"

    result = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        queue_url,
        "--attributes",
        '{"VisibilityTimeout":"47"}',
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
        if after["Attributes"].get("VisibilityTimeout") == "47":
            break
        if time.monotonic() >= deadline:
            assert after["Attributes"].get("VisibilityTimeout") == "47"
        time.sleep(1)