def test_delete_message_nonexistent_queue(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name[-24:]
    )
    existing_name = f"delete-message-existing-{suffix}"
    missing_name = f"delete-message-missing-{suffix}"

    existing_url = sqs.rpc(
        "CreateQueue",
        {"QueueName": existing_name},
    )["QueueUrl"]
    sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": existing_url,
            "MessageBody": "message that must remain",
        },
    )

    missing_url = existing_url.rsplit("/", 1)[0] + "/" + missing_name
    before = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert not any(
        queue_url.endswith("/" + missing_name)
        for queue_url in before.get("QueueUrls", [])
    )

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        missing_url,
        "--receipt-handle",
        "unused-receipt-handle",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": missing_name})
    assert not any(
        queue_url.endswith("/" + missing_name)
        for queue_url in after.get("QueueUrls", [])
    )

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": existing_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )["Attributes"]
    assert attributes["ApproximateNumberOfMessages"] == "1"