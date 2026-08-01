def test_get_queue_attributes_happy_path(cli, sqs, tmp_path):
    import json

    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )[-40:]
    queue_name = "get-queue-attributes-" + suffix

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
    output = json.loads(result.stdout)
    assert isinstance(output, dict)
    if "Attributes" in output:
        assert isinstance(output["Attributes"], dict)

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name)
        for url in listed.get("QueueUrls", [])
    )

    state = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert state["Attributes"]["VisibilityTimeout"] == "47"