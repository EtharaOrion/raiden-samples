def test_purge_queue_missing_required_queue_url(cli, sqs, tmp_path):
    suffix = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )[-50:]
    queue_name = f"purge-invalid-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": queue_name})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + queue_name)

    sent = sqs.rpc(
        "SendMessage",
        {"QueueUrl": queue_url, "MessageBody": "must remain after invalid command"},
    )
    assert sent.get("MessageId")

    result = cli("sqs", "purge-queue")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "queue-url" in result.stderr.lower()

    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": queue_name})
    assert any(url.endswith("/" + queue_name) for url in listed.get("QueueUrls", []))

    attributes = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert attributes["Attributes"]["ApproximateNumberOfMessages"] == "1"