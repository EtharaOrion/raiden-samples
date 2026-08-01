def test_send_message_batch_rejects_too_many_entries(cli, sqs, tmp_path):
    import hashlib
    import json

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:20]
    queue_name = f"batch-too-many-{suffix}"
    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]

    entries = [
        {"Id": f"entry-{index}", "MessageBody": f"message-{index}"}
        for index in range(11)
    ]

    result = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "TooManyEntriesInBatchRequest" in result.stderr

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith(f"/{queue_name}") for url in listed.get("QueueUrls", [])
    )

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": [
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
                "ApproximateNumberOfMessagesDelayed",
            ],
        },
    )["Attributes"]
    assert attributes["ApproximateNumberOfMessages"] == "0"
    assert attributes["ApproximateNumberOfMessagesNotVisible"] == "0"
    assert attributes["ApproximateNumberOfMessagesDelayed"] == "0"