def test_delete_message_duplicate_queue_url_is_rejected_without_deleting_message(cli, sqs, tmp_path):
    suffix = "".join(char if char.isalnum() else "-" for char in tmp_path.name)
    queue_name = ("delete-message-invalid-args-" + suffix)[:80]

    queue_url = sqs.rpc("CreateQueue", {"QueueName": queue_name})["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": "message-must-remain",
        },
    )

    baseline = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert baseline["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli(
        "sqs",
        "delete-message",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        "not-a-valid-receipt-handle",
        "--queue-url",
        queue_url,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "ReceiptHandleIsInvalid" in result.stderr
        or "InvalidIdFormat" in result.stderr
        or "Unknown options" in result.stderr
        or "argument --queue-url" in result.stderr
    )

    resulting = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert resulting["Attributes"]["ApproximateNumberOfMessages"] == "1"