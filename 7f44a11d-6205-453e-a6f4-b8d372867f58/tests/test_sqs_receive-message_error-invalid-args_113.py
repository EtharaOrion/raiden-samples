def test_receive_message_nonexistent_queue_errors(cli, sqs):
    # Prerequisite: ensure a queue exists so we can derive a valid URL shape,
    # then target a queue name that does not exist.
    existing = sqs.rpc("CreateQueue", {"QueueName": "seed-queue-for-receive-test"})
    existing_url = existing["QueueUrl"]
    assert existing_url.endswith("/seed-queue-for-receive-test")

    # Build a URL for a queue that definitely does not exist.
    missing_name = "definitely-missing-queue-xyz"
    missing_url = existing_url.rsplit("/", 1)[0] + "/" + missing_name

    # Confirm the missing queue really is absent.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert missing_name not in "".join(listed.get("QueueUrls", []))

    result = cli("sqs", "receive-message", "--queue-url", missing_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the missing queue was not created as a side effect.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert missing_name not in "".join(listed_after.get("QueueUrls", []))