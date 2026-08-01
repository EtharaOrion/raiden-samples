def test_delete_message_error_nonexistent(cli, sqs):
    # Prerequisite: create then delete a queue so its URL is well-formed but nonexistent
    queue_name = "nonexistent-dm-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})

    # Confirm it's gone
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_url not in listed.get("QueueUrls", [])

    # Run command under test against the nonexistent queue
    result = cli(
        "sqs", "delete-message",
        "--queue-url", queue_url,
        "--receipt-handle", "some-bogus-receipt-handle",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Queue still absent
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_url not in listed_after.get("QueueUrls", [])