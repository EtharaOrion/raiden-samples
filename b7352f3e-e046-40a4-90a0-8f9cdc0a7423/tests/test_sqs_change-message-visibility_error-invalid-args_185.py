def test_change_message_visibility_rejects_unknown_attribute_definitions(cli, sqs, tmp_path):
    import hashlib

    suffix = hashlib.sha256(str(tmp_path).encode()).hexdigest()[:16]
    queue_name = f"cmv-invalid-args-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sqs.rpc(
        "SendMessage",
        {
            "QueueUrl": queue_url,
            "MessageBody": "message must remain unchanged",
        },
    )

    before = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert before["Attributes"]["ApproximateNumberOfMessages"] == "1"

    result = cli(
        "sqs",
        "change-message-visibility",
        "--queue-url",
        queue_url,
        "--receipt-handle",
        "unused-invalid-receipt-handle",
        "--visibility-timeout",
        "10",
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
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "1"

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))