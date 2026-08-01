def test_get_queue_attributes_rejects_invalid_attribute_definitions(cli, sqs, tmp_path):
    queue_name = ("get-attrs-invalid-" + tmp_path.name)[-80:]
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    result = cli(
        "sqs",
        "get-queue-attributes",
        "--queue-url",
        queue_url,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name) for url in listed.get("QueueUrls", [])
    )