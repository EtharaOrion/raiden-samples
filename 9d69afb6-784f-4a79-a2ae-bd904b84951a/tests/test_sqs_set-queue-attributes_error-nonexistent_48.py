def test_set_queue_attributes_nonexistent_queue(cli, sqs):
    # Build a queue URL for a queue that does not exist by deriving the
    # account path from a real queue, then pointing at a missing name.
    real = sqs.rpc("CreateQueue", {"QueueName": "seed-existing-queue"})
    real_url = real["QueueUrl"]
    # Replace trailing queue name with a non-existent one, keeping the account path.
    missing_url = real_url.rsplit("/", 1)[0] + "/definitely-missing-queue-xyz"

    # Sanity: the missing queue is not present.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": "definitely-missing-queue-xyz"})
    assert missing_url not in listed.get("QueueUrls", [])

    result = cli(
        "sqs", "set-queue-attributes",
        "--queue-url", missing_url,
        "--attributes", '{"VisibilityTimeout":"45"}',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the missing queue still doesn't exist.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": "definitely-missing-queue-xyz"})
    assert missing_url not in listed_after.get("QueueUrls", [])