def test_get_queue_attributes_happy_path(cli, sqs):
    queue_name = "test-gqa-happy-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs", "get-queue-attributes",
        "--queue-url", queue_url,
        "--attribute-names", "All",
    )
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    assert "Attributes" in payload
    cli_attrs = payload["Attributes"]

    server = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["All"],
    })
    server_attrs = server["Attributes"]

    assert "QueueArn" in server_attrs
    assert server_attrs["QueueArn"].endswith(queue_name)
    assert cli_attrs.get("QueueArn") == server_attrs["QueueArn"]