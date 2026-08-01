def test_get_queue_attributes_invalid_queue_url(cli, sqs):
    bogus_url = "x" * 500
    result = cli("sqs", "get-queue-attributes", "--queue-url", bogus_url)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert (
        "invalidaddress" in stderr
        or "nonexistentqueue" in stderr
        or "queuedoesnotexist" in stderr
        or "invalid" in stderr
        or "exception" in stderr
    )
    listed = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert bogus_url not in listed