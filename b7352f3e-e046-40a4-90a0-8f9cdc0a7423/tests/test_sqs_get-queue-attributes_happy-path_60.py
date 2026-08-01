def test_get_queue_attributes_happy_path(cli, sqs, tmp_path):
    queue_name = "attrs-" + "".join(
        char if char.isalnum() or char in "-_" else "-"
        for char in tmp_path.name
    )[:70]
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

    observed = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["All"],
        },
    )
    assert observed["Attributes"]["VisibilityTimeout"] == "47"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name)
        for url in listed.get("QueueUrls", [])
    )