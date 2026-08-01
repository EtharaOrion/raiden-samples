def test_receive_message_rejects_invalid_attribute_definitions(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-40:]
    queue_name = f"receive-invalid-args-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "must remain visible"},
    )
    assert sent["MessageId"]

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": [
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
            ],
        },
    )["Attributes"]
    assert before["ApproximateNumberOfMessages"] == "1"
    assert before["ApproximateNumberOfMessagesNotVisible"] == "0"

    result = cli(
        "sqs",
        "receive-message",
        "--queue-url",
        queue_url,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": [
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
            ],
        },
    )["Attributes"]
    assert after["ApproximateNumberOfMessages"] == "1"
    assert after["ApproximateNumberOfMessagesNotVisible"] == "0"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(
        url.endswith("/" + queue_name)
        for url in listed.get("QueueUrls", [])
    )