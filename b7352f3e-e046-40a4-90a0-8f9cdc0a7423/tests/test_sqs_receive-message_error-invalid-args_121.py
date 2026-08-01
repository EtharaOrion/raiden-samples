def test_receive_message_missing_required_queue_url(cli, sqs, tmp_path):
    queue_name = f"receive-invalid-{abs(hash(str(tmp_path)))}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "must remain unreceived"},
    )
    assert sent["MessageId"]
    assert sent["MD5OfMessageBody"]

    result = cli("sqs", "receive-message")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--queue-url" in result.stderr

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert attributes["Attributes"]["ApproximateNumberOfMessages"] == "1"