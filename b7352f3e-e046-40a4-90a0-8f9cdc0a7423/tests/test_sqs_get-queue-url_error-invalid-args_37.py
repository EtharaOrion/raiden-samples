def test_get_queue_url_rejects_unknown_attribute_definitions(cli, sqs, tmp_path):
    suffix = "".join(character for character in tmp_path.name if character.isalnum())
    queue_name = ("get-queue-url-invalid-" + suffix)[-80:]

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith("/" + queue_name)

    result = cli(
        "sqs",
        "get-queue-url",
        "--queue-name",
        queue_name,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        queue_url.endswith("/" + queue_name)
        for queue_url in queues.get("QueueUrls", [])
    )