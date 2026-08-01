def test_send_message_batch_enqueues_all_messages(cli, sqs, tmp_path):
    import json

    suffix = "".join(
        character if character.isalnum() else "-"
        for character in tmp_path.name
    )[-50:]
    queue_name = f"send-message-batch-{suffix}"

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

    entries = [
        {"Id": "first", "MessageBody": "first batch message"},
        {"Id": "second", "MessageBody": "second batch message"},
    ]
    result = cli(
        "sqs",
        "send-message-batch",
        "--queue-url",
        queue_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    successful = {item["Id"]: item for item in response.get("Successful", [])}
    assert set(successful) == {"first", "second"}
    assert all(successful[entry_id].get("MessageId") for entry_id in successful)
    assert response.get("Failed", []) == []

    after = sqs.rpc(
        "GetQueueAttributes",
        {
            "QueueUrl": queue_url,
            "AttributeNames": ["ApproximateNumberOfMessages"],
        },
    )
    assert after["Attributes"]["ApproximateNumberOfMessages"] == "2"