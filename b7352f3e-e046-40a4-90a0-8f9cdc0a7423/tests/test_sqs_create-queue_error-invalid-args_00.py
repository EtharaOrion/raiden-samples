def test_create_queue_missing_required_queue_name(cli, sqs, tmp_path):
    marker_name = f"invalid-args-marker-{abs(hash(str(tmp_path)))}"
    created = sqs.rpc("CreateQueue", {"QueueName": marker_name})
    assert created["QueueUrl"].endswith("/" + marker_name)

    before = set(sqs.rpc("ListQueues", {}).get("QueueUrls", []))
    assert any(url.endswith("/" + marker_name) for url in before)

    result = cli("sqs", "create-queue")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--queue-name" in result.stderr

    after = set(sqs.rpc("ListQueues", {}).get("QueueUrls", []))
    assert after == before
    assert any(url.endswith("/" + marker_name) for url in after)