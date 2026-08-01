def test_delete_queue_invalid_args(cli, sqs, tmp_path):
    queue_name = "test-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    result = cli(
        "sqs", "delete-queue",
        "--queue-url", queue_url,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    # The queue must still exist since the command was rejected
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    urls = listed.get("QueueUrls", []) or []
    assert any(u.endswith("/" + queue_name) for u in urls)

    # cleanup
    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})