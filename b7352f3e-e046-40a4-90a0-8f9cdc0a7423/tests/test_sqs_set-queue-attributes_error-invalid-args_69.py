def test_set_queue_attributes_missing_attributes_fails_without_changing_queue(cli, sqs, tmp_path):
    import uuid

    queue_name = f"set-attributes-invalid-{uuid.uuid4().hex}"
    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "37"},
        },
    )
    queue_url = created["QueueUrl"]

    result = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        queue_url,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--attributes" in result.stderr

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert attributes["Attributes"]["VisibilityTimeout"] == "37"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))