def test_send_message_batch_requires_entries(cli, sqs, tmp_path):
    suffix = "".join(char if char.isalnum() else "-" for char in tmp_path.name)[-40:]
    queue_name = f"missing-entries-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    result = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        queue_url,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--entries" in result.stderr

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert attributes["Attributes"]["ApproximateNumberOfMessages"] == "0"