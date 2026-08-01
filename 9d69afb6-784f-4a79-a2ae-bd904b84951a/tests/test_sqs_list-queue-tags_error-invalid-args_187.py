def test_list_queue_tags_invalid_args(cli, sqs):
    queue_name = "test-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs", "list-queue-tags",
        "--queue-url", queue_url,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "argument" in result.stderr.lower() or "unknown" in result.stderr.lower() or "Error" in result.stderr

    # Queue still exists and is unaffected
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})