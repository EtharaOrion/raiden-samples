def test_receive_message_nonexistent_queue_errors(cli, sqs):
    # Prerequisite: ensure a clean, known base queue exists so the server is live,
    # but target a queue URL that does not exist for the receive-message call.
    base_name = "seed-queue-for-receive-error"
    base_url = sqs.rpc("CreateQueue", {"QueueName": base_name})["QueueUrl"]
    assert base_url.endswith("/" + base_name)

    # Construct a URL to a queue that does not exist by reusing the base URL's
    # path prefix but with a missing queue name.
    missing_name = "definitely-missing-queue-xyz"
    missing_url = base_url.rsplit("/", 1)[0] + "/" + missing_name

    # Confirm it truly does not exist.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name}).get("QueueUrls", [])
    assert missing_url not in listed

    # Run the command under test against the missing queue.
    result = cli("sqs", "receive-message", "--queue-url", missing_url)

    # Must fail with the service error category surfaced in stderr.
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the missing queue still does not exist after the failed call.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name}).get("QueueUrls", [])
    assert missing_url not in listed_after