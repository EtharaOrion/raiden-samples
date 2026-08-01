def test_change_message_visibility_batch_requires_entries(cli, sqs, tmp_path):
    import uuid

    queue_name = f"visibility-batch-{uuid.uuid4().hex}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith(f"/{queue_name}")

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "message-must-remain-available"},
    )
    assert sent["MessageId"]

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
        "--queue-url",
        queue_url,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--entries" in result.stderr

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
        url.endswith(f"/{queue_name}") for url in listed.get("QueueUrls", [])
    )