def test_delete_message_batch_requires_queue_url(cli, sqs, tmp_path):
    import json

    queue_name = "delete-batch-" + tmp_path.name.replace("_", "-")[-50:]
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "must remain queued"},
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"]

    before = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli(
        "sqs",
        "delete-message-batch",
        "--entries",
        json.dumps([{"Id": "entry-1", "ReceiptHandle": "unused-handle"}]),
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    after = sqs.rpc(
        "GetQueueAttributes",
        {"QueueUrl": queue_url, "AttributeNames": ["ApproximateNumberOfMessages"]},
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))