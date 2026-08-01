def test_delete_message_batch_nonexistent_queue(cli, sqs, tmp_path):
    import json
    import uuid

    suffix = uuid.uuid4().hex
    missing_name = f"delete-batch-missing-{suffix}"
    witness_name = f"delete-batch-witness-{suffix}"

    missing_url = sqs.rpc("CreateQueue", {"QueueName": missing_name})["QueueUrl"]
    witness_url = sqs.rpc("CreateQueue", {"QueueName": witness_name})["QueueUrl"]
    sqs.rpc("DeleteQueue", {"QueueUrl": missing_url})

    before = sqs.rpc("ListQueues", {})
    before_urls = before.get("QueueUrls", [])
    assert not any(url.endswith("/" + missing_name) for url in before_urls)
    assert any(url.endswith("/" + witness_name) for url in before_urls)

    entries = [{"Id": "entry-1", "ReceiptHandle": "invalid-receipt-handle"}]
    result = cli(
        "sqs",
        "delete-message-batch",
        "--queue-url",
        missing_url,
        "--entries",
        json.dumps(entries),
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    after = sqs.rpc("ListQueues", {})
    after_urls = after.get("QueueUrls", [])
    assert not any(url.endswith("/" + missing_name) for url in after_urls)
    assert any(url.endswith("/" + witness_name) for url in after_urls)