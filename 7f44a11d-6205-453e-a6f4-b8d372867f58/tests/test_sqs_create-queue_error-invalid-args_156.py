def test_create_queue_invalid_name_rejected(cli, sqs):
    bad_name = "invalid name with spaces!"
    result = cli("sqs", "create-queue", "--queue-name", bad_name)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "InvalidParameterValue" in result.stderr or "InvalidAddress" in result.stderr \
        or "InvalidAttributeName" in result.stderr or "InvalidAttributeValue" in result.stderr \
        or "Exception" in result.stderr
    listed = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert not any(url.endswith("/" + bad_name) for url in listed)