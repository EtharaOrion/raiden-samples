def test_get_queue_attributes_invalid_queue_url(cli, sqs):
    bogus_name = "x" * 500
    bogus_url = "http://localhost:9324/000000000000/" + bogus_name

    result = cli("sqs", "get-queue-attributes", "--queue-url", bogus_url)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "NonExistent" in result.stderr \
        or "NotFound" in result.stderr or "InvalidAddress" in result.stderr \
        or "QueueDoesNotExist" in result.stderr

    listed = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert not any(u.endswith("/" + bogus_name) for u in listed)