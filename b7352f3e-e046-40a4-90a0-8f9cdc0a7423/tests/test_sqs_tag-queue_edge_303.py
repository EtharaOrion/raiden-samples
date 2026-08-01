import uuid


def test_tag_queue_edge_add_then_untag_roundtrip(cli, sqs):
    qname = "edge-tag-rt-" + uuid.uuid4().hex[:16]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    r1 = cli(
        "sqs", "tag-queue",
        "--queue-url", url,
        "--tags", '{"env":"stage","owner":"alice","team":"payments"}',
    )
    assert r1.returncode == 0

    got = sqs.rpc("ListQueueTags", {"QueueUrl": url}).get("Tags") or {}
    assert got.get("env") == "stage"
    assert got.get("owner") == "alice"
    assert got.get("team") == "payments"

    r2 = cli(
        "sqs", "untag-queue",
        "--queue-url", url,
        "--tag-keys", "env", "owner",
    )
    assert r2.returncode == 0

    after = sqs.rpc("ListQueueTags", {"QueueUrl": url}).get("Tags") or {}
    assert "env" not in after
    assert "owner" not in after
    assert after.get("team") == "payments"
