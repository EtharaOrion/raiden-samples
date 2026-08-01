def test_send_message_invalid_queue_url(cli, sqs):
    bogus_queue_name = "x" * 400
    bogus_url = f"http://localhost:9324/000000000000/{bogus_queue_name}"

    result = cli(
        "sqs", "send-message",
        "--queue-url", bogus_url,
        "--message-body", "hello world",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr
    assert (
        "NonExistentQueue" in stderr
        or "QueueDoesNotExist" in stderr
        or "InvalidAddress" in stderr
        or "Exception" in stderr
    )

    # Assert no such queue exists in the backend
    listed = sqs.rpc("ListQueues", {})
    urls = listed.get("QueueUrls", []) or []
    assert not any(u.endswith(bogus_queue_name) for u in urls)