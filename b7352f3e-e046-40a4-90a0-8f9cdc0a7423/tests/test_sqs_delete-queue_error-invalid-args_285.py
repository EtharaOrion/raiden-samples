def test_delete_queue_rejects_unknown_flag_without_deleting_queue(cli, sqs, tmp_path):
    suffix = "".join(char if char.isalnum() else "-" for char in tmp_path.name)
    queue_name = f"invalid-delete-{suffix}"[:80]

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs",
        "delete-queue",
        "--queue-url",
        queue_url,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith("/" + queue_name) for url in queues)