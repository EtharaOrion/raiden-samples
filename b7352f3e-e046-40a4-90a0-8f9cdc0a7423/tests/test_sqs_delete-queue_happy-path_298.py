def test_delete_queue_removes_existing_queue(cli, sqs, tmp_path):
    import time

    suffix = "".join(
        character if character.isalnum() else "-"
        for character in str(tmp_path)
    )[-48:]
    queue_name = f"delete-queue-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name)
        for url in before.get("QueueUrls", [])
    )

    result = cli("sqs", "delete-queue", "--queue-url", queue_url)
    assert result.returncode == 0

    deadline = time.monotonic() + 65
    while True:
        after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
        queue_still_exists = any(
            url.endswith("/" + queue_name)
            for url in after.get("QueueUrls", [])
        )
        if not queue_still_exists or time.monotonic() >= deadline:
            break
        time.sleep(1)

    assert not queue_still_exists