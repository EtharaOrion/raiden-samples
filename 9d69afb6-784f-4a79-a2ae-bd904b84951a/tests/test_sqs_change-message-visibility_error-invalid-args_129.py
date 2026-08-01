def test_change_message_visibility_invalid_empty_queue_url(cli, sqs):
    # Seed a real queue so the account/state exists, unrelated to the invalid call.
    qname = "cmv-invalid-args-queue"
    created = sqs.rpc("CreateQueue", {"QueueName": qname})
    queue_url = created["QueueUrl"]
    assert queue_url.endswith("/" + qname)

    # Invoke with an empty queue-url (invalid argument).
    result = cli(
        "sqs", "change-message-visibility",
        "--queue-url", "",
        "--receipt-handle", "some-bogus-handle",
        "--visibility-timeout", "30",
    )

    # Must fail with an error category in stderr.
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert (
        "invalidaddress" in stderr
        or "queuedoesnotexist" in stderr
        or "nonexistentqueue" in stderr
        or "invalid" in stderr
        or "error" in stderr
    )

    # State assertion: the seeded queue is unaffected and still present.
    listed = sqs.rpc("ListQueues", {"QueueNamePrefix": qname})
    assert any(u.endswith("/" + qname) for u in listed.get("QueueUrls", []))

    sqs.rpc("DeleteQueue", {"QueueUrl": queue_url})