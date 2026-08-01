def test_delete_message_invalid_args(cli, sqs, tmp_path):
    queue_name = "test-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    # Send a message so there is real state to potentially delete
    sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})

    # Invoke delete-message with an unknown flag / invalid JSON argument
    result = cli(
        "sqs", "delete-message",
        "--queue-url", queue_url,
        "--receipt-handle", "some-handle",
        "--attribute-definitions", "{not valid json",
    )

    # This is an argument-parsing error; must fail
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "argument" in result.stderr.lower()

    # State unchanged: the message should still be present (nothing deleted)
    attrs = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })["Attributes"]
    assert int(attrs["ApproximateNumberOfMessages"]) == 1