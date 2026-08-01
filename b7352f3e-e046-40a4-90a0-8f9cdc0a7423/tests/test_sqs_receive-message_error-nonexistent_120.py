def test_receive_message_nonexistent_queue(cli, sqs, tmp_path):
    token = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-30:]
    anchor_name = f"receive-anchor-{token}"
    missing_name = f"receive-missing-{token}"

    anchor_url = sqs.rpc(
        "CreateQueue",
        {"QueueName": anchor_name},
    )["QueueUrl"]
    missing_url = f"{anchor_url.rsplit('/', 1)[0]}/{missing_name}"

    result = cli(
        "sqs",
        "receive-message",
        "--queue-url",
        missing_url,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    queues = sqs.rpc(
        "ListQueues",
        {"QueueNamePrefix": missing_name},
    ).get("QueueUrls", [])
    assert not any(url.endswith(f"/{missing_name}") for url in queues)