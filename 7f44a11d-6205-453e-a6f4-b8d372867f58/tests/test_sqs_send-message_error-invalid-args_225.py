def test_send_message_nonexistent_queue_error(cli, sqs):
    prefix = "test-sendmsg-missing-"
    queue_name = prefix + "queue"

    # Ensure the queue does not exist beforehand.
    existing = sqs.rpc("ListQueues", {"QueueNamePrefix": prefix}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in existing)

    # Construct a URL pointing at a non-existent queue on the same endpoint.
    bogus_url = "http://localhost:9324/000000000000/" + queue_name

    result = cli(
        "sqs",
        "send-message",
        "--queue-url",
        bogus_url,
        "--message-body",
        "hello world",
    )

    # The command must fail.
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the queue still does not exist.
    after = sqs.rpc("ListQueues", {"QueueNamePrefix": prefix}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in after)