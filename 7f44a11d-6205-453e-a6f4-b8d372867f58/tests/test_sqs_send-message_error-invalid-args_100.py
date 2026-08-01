def test_send_message_nonexistent_queue_error(cli, sqs, tmp_path):
    queue_name = "test-send-msg-missing-queue"
    # Establish prerequisite: create then delete so the URL is well-formed but missing
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)
    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})

    # Run the command under test against the now-missing queue
    result = cli(
        "sqs", "send-message",
        "--queue-url", queue_url,
        "--message-body", "hello world",
    )

    # Must fail with an error category surfaced in stderr
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert resulting state: queue still does not exist
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_name not in "".join(listed.get("QueueUrls", []))