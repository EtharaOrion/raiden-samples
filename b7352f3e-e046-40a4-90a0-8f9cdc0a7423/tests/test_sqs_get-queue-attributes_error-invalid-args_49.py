def test_get_queue_attributes_requires_queue_url(cli, sqs, tmp_path):
    queue_name = "get-attributes-" + tmp_path.name.replace("_", "-")
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    assert created["QueueUrl"].endswith("/" + queue_name)

    result = cli("sqs", "get-queue-attributes")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    matching_urls = [
        url
        for url in queues.get("QueueUrls", [])
        if url.endswith("/" + queue_name)
    ]
    assert len(matching_urls) == 1