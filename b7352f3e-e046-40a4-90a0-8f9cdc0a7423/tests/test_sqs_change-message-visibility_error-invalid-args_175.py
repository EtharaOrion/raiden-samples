def test_change_message_visibility_requires_queue_url(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )[-40:]
    queue_name = f"cmv-missing-url-{suffix}"

    created = sqs.rpc(
        "CreateQueue",
        {
            "QueueName": queue_name,
            "Attributes": {"VisibilityTimeout": "45"},
        },
    )
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "message must remain queued"},
    )
    assert sent["MessageId"]

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": [
                "ApproximateNumberOfMessages",
                "VisibilityTimeout",
            ],
        },
    )["Attributes"]
    assert before["ApproximateNumberOfMessages"] == "1"
    assert before["VisibilityTimeout"] == "45"

    result = cli(
        "sqs",
        "change-message-visibility",
        "--receipt-handle",
        "unused-receipt-handle",
        "--visibility-timeout",
        "10",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--queue-url" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": [
                "ApproximateNumberOfMessages",
                "VisibilityTimeout",
            ],
        },
    )["Attributes"]
    assert after["ApproximateNumberOfMessages"] == before["ApproximateNumberOfMessages"]
    assert after["VisibilityTimeout"] == before["VisibilityTimeout"]

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name) for url in listed.get("QueueUrls", [])
    )