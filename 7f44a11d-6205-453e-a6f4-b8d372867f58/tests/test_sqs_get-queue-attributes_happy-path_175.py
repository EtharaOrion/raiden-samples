def test_get_queue_attributes_happy_path(cli, sqs):
    queue_name = "test_gqa_happy_v4"
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
    attrs = payload["Attributes"]

    server_attrs = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["All"]},
    )["Attributes"]

    assert attrs.get("QueueArn") == server_attrs.get("QueueArn")
    assert attrs["QueueArn"].endswith(queue_name)