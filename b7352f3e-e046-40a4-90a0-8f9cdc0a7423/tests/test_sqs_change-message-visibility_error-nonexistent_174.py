def test_change_message_visibility_nonexistent_queue(cli, sqs, tmp_path):
    suffix = "".join(ch if ch.isalnum() else "-" for ch in tmp_path.name)[-40:]
    existing_name = f"cmv-existing-{suffix}"
    missing_name = f"cmv-missing-{suffix}"

    created = sqs.rpc("CreateQueue", {"QueueName": existing_name})
    existing_url = created["QueueUrl"]
    assert existing_url.endswith("/" + existing_name)

    missing_url = existing_url.rsplit("/", 1)[0] + "/" + missing_name
    before = sqs.rpc("ListQueues", {})
    before_urls = before.get("QueueUrls", [])
    assert any(url.endswith("/" + existing_name) for url in before_urls)
    assert not any(url.endswith("/" + missing_name) for url in before_urls)

    result = cli(
        "sqs",
        "change-message-visibility",
        "--queue-url",
        missing_url,
        "--receipt-handle",
        "nonexistent-receipt-handle",
        "--visibility-timeout",
        "60",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "QueueDoesNotExist" in result.stderr

    after = sqs.rpc("ListQueues", {})
    after_urls = after.get("QueueUrls", [])
    assert any(url.endswith("/" + existing_name) for url in after_urls)
    assert not any(url.endswith("/" + missing_name) for url in after_urls)