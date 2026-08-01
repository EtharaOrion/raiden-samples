def test_delete_message_batch_rejects_invalid_entries_without_deleting(cli, sqs, tmp_path):
    queue_name = f"delete-batch-invalid-{tmp_path.name}".replace("_", "-")
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "message-must-remain"},
    )
    assert sent.get("MessageId")

    before = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        "[{",
        "--queue-url",
        queue_url,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid JSON" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"