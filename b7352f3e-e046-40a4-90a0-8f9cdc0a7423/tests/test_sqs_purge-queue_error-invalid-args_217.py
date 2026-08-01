def test_purge_queue_invalid_attribute_definitions_preserves_messages(cli, sqs, tmp_path):
    queue_name = "purge-invalid-" + str(abs(hash(str(tmp_path))))
    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "must-not-be-purged"},
    )
    assert sent.get("MessageId")

    result = cli(
        "sqs",
        "purge-queue",
        "--queue-url",
        queue_url,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown option" in result.stderr

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert attributes["Attributes"]["ApproximateNumberOfMessages"] == "1"