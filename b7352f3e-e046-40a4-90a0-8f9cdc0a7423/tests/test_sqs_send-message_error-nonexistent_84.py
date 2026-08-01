def test_send_message_nonexistent_queue(cli, sqs, tmp_path):
    token = "".join(
        character if character.isalnum() or character in "-_" else "-"
        for character in tmp_path.name
    )[-30:]
    sentinel_name = f"send-error-sentinel-{token}"
    missing_name = f"send-error-missing-{token}"

    created = sqs.rpc("CreateQueue", {"QueueName": sentinel_name})
    sentinel_url = created["QueueUrl"]
    missing_url = sentinel_url.rsplit("/", 1)[0] + "/" + missing_name

    before = sqs.rpc("ListQueues", {"QueueNamePrefix": "send-error-"})
    before_urls = before.get("QueueUrls", [])
    assert any(url.endswith("/" + sentinel_name) for url in before_urls)
    assert not any(url.endswith("/" + missing_name) for url in before_urls)

    result = cli(
        "sqs",
        "send-message",
        "--queue-url",
        missing_url,
        "--message-body",
        "message for a queue that does not exist",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    after = sqs.rpc("ListQueues", {"QueueNamePrefix": "send-error-"})
    after_urls = after.get("QueueUrls", [])
    assert any(url.endswith("/" + sentinel_name) for url in after_urls)
    assert not any(url.endswith("/" + missing_name) for url in after_urls)
    assert set(after_urls) == set(before_urls)