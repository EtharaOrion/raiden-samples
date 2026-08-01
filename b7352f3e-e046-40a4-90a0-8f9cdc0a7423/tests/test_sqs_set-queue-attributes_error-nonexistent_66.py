def test_set_queue_attributes_error_nonexistent(cli, sqs, tmp_path):
    existing_name = f"{tmp_path.name}-existing"
    missing_name = f"{tmp_path.name}-missing"

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": existing_name,
            "Attributes": {"VisibilityTimeout": "30"},
        },
    )
    existing_url = created["QueueUrl"]
    missing_url = f"{existing_url.rsplit('/', 1)[0]}/{missing_name}"

    result = cli(
        "sqs",
        "set-queue-attributes",
        "--queue-url",
        missing_url,
        "--attributes",
        '{"VisibilityTimeout":"45"}',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "QueueDoesNotExist" in result.stderr

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert not any(
        url.endswith(f"/{missing_name}") for url in queues.get("QueueUrls", [])
    )

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": existing_url,
            "AttributeNames": ["VisibilityTimeout"],
        },
    )
    assert attributes["Attributes"]["VisibilityTimeout"] == "30"