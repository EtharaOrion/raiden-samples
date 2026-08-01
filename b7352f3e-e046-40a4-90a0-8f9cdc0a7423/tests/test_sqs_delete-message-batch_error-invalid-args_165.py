def test_delete_message_batch_rejects_unknown_attribute_definitions(cli, sqs, tmp_path):
    import json

    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-40:]
    queue_name = f"delete-batch-invalid-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": "message-must-remain",
        },
    )

    result = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps([{"Id": "entry-1", "ReceiptHandle": "unused-handle"}]),
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