def test_delete_message_missing_queue_url(cli, sqs, tmp_path):
    import hashlib

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:12]
    queue_name = f"delete-message-{suffix}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]

    sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": "message-must-remain",
        },
    )
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
        "delete-message",
        "--receipt-handle",
        "<string>",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--queue-url" in result.stderr

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name}).get("QueueUrls", [])
    assert any(url.endswith("/" + queue_name) for url in queues)

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"