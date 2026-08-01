def test_tag_queue_edge_untag_roundtrip_via_list_queue_tags(cli, sqs):
    import json
    import uuid

    qname = "edge-tag-untag-rt-" + uuid.uuid4().hex[:12]
    url = sqs.rpc("CreateQueue", {"QueueName": qname})["QueueUrl"]

    # Apply two tags via the CLI.
    r = cli(
        "sqs", "tag-queue",
        "--queue-url", url,
        "--tags", '{"env":"stage","team":"core"}',
    )
    assert r.returncode == 0

    tags_after_add = sqs.rpc("ListQueueTags", {"QueueUrl": url}).get("Tags", {})
    assert tags_after_add.get("env") == "stage"
    assert tags_after_add.get("team") == "core"

    # Remove only one of them via the CLI.
    r = cli(
        "sqs", "untag-queue",
        "--queue-url", url,
        "--tag-keys", "env",
    )
    assert r.returncode == 0

    tags_after_rm = sqs.rpc("ListQueueTags", {"QueueUrl": url}).get("Tags", {})
    assert "env" not in tags_after_rm
    assert tags_after_rm.get("team") == "core"

    sqs.rpc("DeleteQueue", {"QueueUrl": url})
