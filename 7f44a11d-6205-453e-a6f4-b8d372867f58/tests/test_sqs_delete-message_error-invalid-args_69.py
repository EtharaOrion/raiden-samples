def test_delete_message_invalid_args(cli, sqs, tmp_path):
    queue_name = "test-delete-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    # Seed a real message so the queue has known state
    send = sqs.rpc("SendMessage", {"QueueUrl": queue_url, "MessageBody": "hello"})
    assert "MessageId" in send

    before = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli(
        "sqs", "delete-message",
        "--queue-url", queue_url,
        "--receipt-handle", "some-receipt-handle",
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Error" in result.stderr or "argument" in result.stderr.lower() \
        or "Unknown" in result.stderr or "Invalid" in result.stderr

    # The invalid invocation must not have mutated queue state
    after = sqs.rpc("GetQueueAttributes", {
        "QueueUrl": queue_url,
        "AttributeNames": ["ApproximateNumberOfMessages"],
    })
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})