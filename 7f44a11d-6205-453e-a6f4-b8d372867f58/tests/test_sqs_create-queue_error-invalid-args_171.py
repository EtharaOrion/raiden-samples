def test_create_queue_invalid_name_rejected(cli, sqs):
    bad_name = "invalid queue name!@#"

    result = cli("sqs", "create-queue", "--queue-name", bad_name)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert (
        "invalidaddress" in stderr
        or "invalidparametervalue" in stderr
        or "invalid" in stderr
    )

    listed = sqs.rpc("ListQueues", {})
    urls = listed.get("QueueUrls", []) or []
    assert not any(u.endswith("/" + bad_name) for u in urls)