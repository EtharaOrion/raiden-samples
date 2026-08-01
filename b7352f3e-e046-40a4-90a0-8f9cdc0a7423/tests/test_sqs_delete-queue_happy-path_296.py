def test_delete_queue_removes_existing_queue(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )
    queue_name = ("delete-queue-" + suffix)[:80]

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.rstrip("/").endswith("/" + queue_name)

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.rstrip("/").endswith("/" + queue_name)
        for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.rstrip("/").endswith("/" + queue_name)
        for url in after.get("QueueUrls", [])
    )