import json


def test_send_message_batch_nonexistent_queue(cli, sqs):
    # Use a queue URL for a queue that does not exist
    bogus_url = "http://localhost:9324/000000000000/this-queue-does-not-exist-xyz"

    # Ensure it really doesn't exist
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": "this-queue-does-not-exist-xyz"})
    assert not any(
        u.endswith("/this-queue-does-not-exist-xyz")
        for u in listed.get("QueueUrls", [])
    )

    entries = json.dumps(
        [{"Id": "msg1", "MessageBody": "hello"}]
    )

    result = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        bogus_url,
        "--entries",
        entries,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # State assertion: the queue still does not exist afterward
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": "this-queue-does-not-exist-xyz"})
    assert not any(
        u.endswith("/this-queue-does-not-exist-xyz")
        for u in listed_after.get("QueueUrls", [])
    )