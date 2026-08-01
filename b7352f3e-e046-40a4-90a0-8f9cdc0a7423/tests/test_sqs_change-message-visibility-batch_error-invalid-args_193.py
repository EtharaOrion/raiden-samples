def test_change_message_visibility_batch_requires_queue_url(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )
    queue_name = ("visibility-batch-" + suffix)[-80:]

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": "message must remain unchanged",
        },
    )
    assert sent.get("MessageId")

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli(
        "sqs",
        "change-message-visibility-batch",
        "--entries",
        '[{"Id":"entry-1","ReceiptHandle":"unused-handle","VisibilityTimeout":30}]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--queue-url" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name)
        for url in listed.get("QueueUrls", [])
    )