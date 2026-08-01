def test_send_message_nonexistent_queue_errors(cli, sqs):
    # Prerequisite: ensure a base queue exists so the endpoint is live,
    # but target a queue URL that does NOT exist.
    base = sqs.rpc("CreateQueue", {"QueueName": "seed-queue-send-err"})
    base_url = base["QueueUrl"]
    assert base_url.endswith("/seed-queue-send-err")

    # Build a URL to a queue that does not exist by swapping the name.
    missing_url = base_url.rsplit("/", 1)[0] + "/definitely-missing-queue-xyz"

    # Confirm the missing queue really is absent.
    listed = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert not any(u.endswith("/definitely-missing-queue-xyz") for u in listed)

    # Command under test: send to a nonexistent queue -> service error.
    result = cli(
        "sqs", "send-message",
        "--queue-url", missing_url,
        "--message-body", "hello",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the missing queue still does not exist afterwards.
    listed_after = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert not any(u.endswith("/definitely-missing-queue-xyz") for u in listed_after)