def test_get_queue_url_nonexistent(cli, sqs, tmp_path):
    token = "".join(char if char.isalnum() else "-" for char in tmp_path.name)[-40:]
    existing_name = f"existing-{token}"
    missing_name = f"missing-{token}"

    created = sqs.rpc("CreateQueue", {"QueueName": existing_name})
    assert created["QueueUrl"].endswith("/" + existing_name)

    before = sqs.rpc("ListQueues", {})
    before_urls = before.get("QueueUrls", [])
    assert any(url.endswith("/" + existing_name) for url in before_urls)
    assert not any(url.endswith("/" + missing_name) for url in before_urls)

    result = cli(
        "sqs",
        "get-queue-url",
        "--queue-name",
        missing_name,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "QueueDoesNotExist" in result.stderr

    after = sqs.rpc("ListQueues", {})
    after_urls = after.get("QueueUrls", [])
    assert any(url.endswith("/" + existing_name) for url in after_urls)
    assert not any(url.endswith("/" + missing_name) for url in after_urls)