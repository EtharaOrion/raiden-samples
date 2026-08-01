def test_change_message_visibility_batch_too_many_entries(cli, sqs, tmp_path):
    import json

    queue_name = "visibility-batch-" + str(abs(hash(str(tmp_path))))
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

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

    entries = [
        {
            "Id": "entry-%02d" % index,
            "ReceiptHandle": "invalid-receipt-handle-%02d" % index,
            "VisibilityTimeout": 30,
        }
        for index in range(11)
    ]

    result = cli(
        "sqs",
        "change-message-visibility-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "TooManyEntriesInBatchRequest" in result.stderr

    queues = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in queues.get("QueueUrls", []))

    after = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"