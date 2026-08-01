def test_create_queue_happy_path(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-40:]
    queue_name = f"create-queue-{suffix}"

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.endswith(f"/{queue_name}")
        for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "create-queue", "--queue-name", queue_name)
    assert result.returncode == 0

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    matching_urls = [
        url
        for url in after.get("QueueUrls", [])
        if url.endswith(f"/{queue_name}")
    ]
    assert len(matching_urls) == 1

    looked_up = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    assert looked_up["QueueUrl"] == matching_urls[0]
    assert looked_up["QueueUrl"].endswith(f"/{queue_name}")