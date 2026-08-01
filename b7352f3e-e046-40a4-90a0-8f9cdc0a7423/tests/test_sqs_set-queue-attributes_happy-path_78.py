def test_set_queue_attributes_updates_visibility_timeout(cli, sqs, tmp_path):
    import json

    suffix = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in tmp_path.name
    )
    queue_name = f"set-attributes-{suffix}"[:80]

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    current_timeout = before["Attributes"]["VisibilityTimeout"]
    new_timeout = "45" if current_timeout != "45" else "46"

    result = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        queue_url,
        "--attributes",
        json.dumps({"VisibilityTimeout": new_timeout}),
    )
    assert result.returncode == 0

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert after["Attributes"]["VisibilityTimeout"] == new_timeout