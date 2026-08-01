def test_tag_queue_error_nonexistent(cli, sqs, tmp_path):
    import json

    # Prerequisite: ensure the queue does NOT exist by using a bogus URL
    account = "000000000000"
    queue_name = "nonexistent-queue-for-tag-test"
    bogus_url = f"http://localhost:9324/{account}/{queue_name}"

    # Sanity: confirm the queue is not present
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_name not in "".join(listed.get("QueueUrls", []) or [])

    result = cli(
        "sqs", "tag-queue",
        "--queue-url", bogus_url,
        "--tags", json.dumps({"env": "test"}),
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NonExistentQueue" in result.stderr or "QueueDoesNotExist" in result.stderr

    # Confirm state unchanged: queue still absent
    listed_after = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert queue_name not in "".join(listed_after.get("QueueUrls", []) or [])