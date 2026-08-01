def test_create_queue_happy_path(cli, sqs, tmp_path):
    unique_suffix = "".join(
        character if character.isalnum() else "-"
        for character in str(tmp_path)
    )[-60:]
    queue_name = "create-queue-" + unique_suffix

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.rstrip("/").endswith("/" + queue_name)
        for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "create-queue", "--queue-name", queue_name)
    assert result.returncode == 0

    queue = sqs.rpc("GetQueueUrl", {"QueueName": queue_name})
    queue_url = queue["QueueUrl"]
    assert queue_url.rstrip("/").endswith("/" + queue_name)

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.rstrip("/").endswith("/" + queue_name)
        for url in after.get("QueueUrls", [])
    )