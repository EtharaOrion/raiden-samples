def test_send_message_error_nonexistent(cli, sqs):
    # Ensure the queue does not exist by using a name that we don't create.
    queue_name = "nonexistent-queue-for-send-message-test"
    bogus_url = "http://localhost:9324/000000000000/" + queue_name

    # Confirm the queue is truly absent before the operation under test.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in urls)

    result = cli(
        "sqs",
        "send-message",
        "--queue-url",
        bogus_url,
        "--message-body",
        "hello world",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the queue still does not exist afterwards.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls_after = listed_after.get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in urls_after)