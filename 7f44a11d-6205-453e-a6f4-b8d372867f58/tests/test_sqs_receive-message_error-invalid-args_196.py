def test_receive_message_nonexistent_queue_errors(cli, sqs, tmp_path):
    # Prerequisite: create then delete a queue so we have a valid-shaped URL
    # that points to a non-existent queue.
    queue_name = "test-recv-missing-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Delete it so subsequent operations target a missing queue.
    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})

    # Confirm it's gone via ListQueues.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_name not in [u.rsplit("/", 1)[-1] for u in listed.get("QueueUrls", [])]

    # Command under test: receive from the now-missing queue must fail.
    result = cli("sqs", "receive-message", "--queue-url", queue_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Assert resulting state: the queue still does not exist.
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_name not in [u.rsplit("/", 1)[-1] for u in listed_after.get("QueueUrls", [])]