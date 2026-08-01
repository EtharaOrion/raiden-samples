def test_get_queue_attributes_nonexistent(cli, sqs, tmp_path):
    token = "".join(character for character in str(tmp_path) if character.isalnum())[-24:]
    prefix = f"getattrs-{token}"
    existing_name = f"{prefix}-existing"
    missing_name = f"{prefix}-missing"

    created = sqs.rpc("CreateQueue", {"QueueName": existing_name})
    existing_url = created["QueueUrl"]
    assert existing_url.endswith("/" + existing_name)

    before_urls = sqs.rpc(
        "ListQueues", {"QueueNamePrefix": prefix}
    ).get("QueueUrls", [])
    assert any(url.endswith("/" + existing_name) for url in before_urls)
    assert not any(url.endswith("/" + missing_name) for url in before_urls)

    missing_url = existing_url.rsplit("/", 1)[0] + "/" + missing_name
    result = cli(
        "sqs",
        "get-queue-attributes",
        "--queue-url",
        missing_url,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "QueueDoesNotExist" in result.stderr
        or "NonExistentQueue" in result.stderr
    )

    after_urls = sqs.rpc(
        "ListQueues", {"QueueNamePrefix": prefix}
    ).get("QueueUrls", [])
    assert any(url.endswith("/" + existing_name) for url in after_urls)
    assert not any(url.endswith("/" + missing_name) for url in after_urls)