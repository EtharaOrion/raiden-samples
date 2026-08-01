def test_receive_message_invalid_attribute_definitions_arg(cli, sqs):
    queue_name = "test-recv-invalid-arg-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs", "receive-message",
        "--queue-url", queue_url,
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "argument" in result.stderr.lower() or "Unknown" in result.stderr or "Invalid" in result.stderr

    # Queue must still exist and be unaffected
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))