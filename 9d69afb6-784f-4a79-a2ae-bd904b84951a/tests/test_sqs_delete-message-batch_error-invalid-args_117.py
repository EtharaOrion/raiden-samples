def test_delete_message_batch_invalid_args(cli, sqs):
    queue_name = "test-dmb-invalid-args-q"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a message so the queue has known state
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})

    result = cli(
        "sqs", "delete-message-batch",
        "--queue-url", queue_url,
        "--entries", '[{"Id":"m1","ReceiptHandle":"fake-handle"}]',
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "argument" in result.stderr.lower() or "unknown" in result.stderr.lower() or "Error" in result.stderr

    # Queue state unaffected: still exists
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(u.endswith("/" + queue_name) for u in listed.get("QueueUrls", []))