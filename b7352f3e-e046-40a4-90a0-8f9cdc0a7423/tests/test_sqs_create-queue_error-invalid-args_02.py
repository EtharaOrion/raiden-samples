def test_create_queue_rejects_unknown_flag_without_creating_queue(cli, sqs, tmp_path):
    suffix = "".join(character if character.isalnum() else "-" for character in tmp_path.name)
    queue_name = ("invalid-args-" + suffix)[:80]

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.rstrip("/").endswith("/" + queue_name)
        for url in before.get("QueueUrls", [])
    )

    result = cli(
        "sqs",
        "create-queue",
        "--queue-name",
        queue_name,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert not any(
        url.rstrip("/").endswith("/" + queue_name)
        for url in after.get("QueueUrls", [])
    )