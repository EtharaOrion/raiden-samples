import json


def test_send_message_batch_nonexistent_queue(cli, sqs):
    # Prerequisite: ensure the queue does NOT exist by using a bogus URL
    queue_name = "nonexistent-queue-smb-error"
    bogus_url = "http://localhost:9324/000000000000/" + queue_name

    # Sanity: the queue should not be in the list
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in urls)

    entries = json.dumps([{"Id": "m1", "MessageBody": "hello world"}])

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

    # State: the queue still does not exist
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls_after = listed_after.get("QueueUrls", []) or []
    assert not any(u.endswith("/" + queue_name) for u in urls_after)