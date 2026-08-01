def test_receive_message_invalid_queue_url(cli, sqs):
    bogus_url = "https://sqs.us-east-1.amazonaws.com/123456789012/" + ("x" * 500)
    result = cli("sqs", "receive-message", "--queue-url", bogus_url)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr
    assert (
        "NonExistentQueue" in stderr
        or "QueueDoesNotExist" in stderr
        or "InvalidAddress" in stderr
        or "Exception" in stderr
        or "Error" in stderr
    )
    listed = sqs.rpc("ListQueues", {}).get("QueueUrls", []) or []
    assert bogus_url not in listed