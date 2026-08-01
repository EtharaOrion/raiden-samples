def test_send_message_rejects_invalid_message_contents(cli, sqs, tmp_path):
    queue_name = f"invalid-message-{abs(hash(str(tmp_path)))}"
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "0"

    result = cli(
        "sqs",
        "send-message",
        "--queue-url",
        queue_url,
        "--message-body",
        "invalid\x01message",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidMessageContents" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "0"