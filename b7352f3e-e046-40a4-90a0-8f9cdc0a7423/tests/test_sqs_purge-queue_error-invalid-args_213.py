def test_purge_queue_rejects_unknown_flag_without_purging(cli, sqs):
    import uuid

    queue_name = f"purge-invalid-args-{uuid.uuid4().hex}"
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
        "purge-queue",
        "--queue-url",
        queue_url,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith(f"/{queue_name}") for url in listed.get("QueueUrls", []))