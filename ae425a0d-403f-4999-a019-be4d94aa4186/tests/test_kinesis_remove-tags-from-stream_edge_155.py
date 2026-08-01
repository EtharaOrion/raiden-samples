def test_remove_tags_from_stream_removes_seeded_tag(cli, kinesis):
    stream_name = "test-remove-tags-stream-edge"
    tag_key = "x" * 48
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})
    kinesis.rpc("AddTagsToStream", {"StreamName": stream_name, "Tags": {tag_key: "somevalue"}})

    listed = kinesis.rpc("ListTagsForStream", {"StreamName": stream_name})
    keys_before = {t["Key"] for t in listed.get("Tags", [])}
    assert tag_key in keys_before

    result = cli(
        "kinesis", "remove-tags-from-stream",
        "--stream-name", stream_name,
        "--tag-keys", tag_key,
    )
    assert result.returncode == 0

    after = kinesis.rpc("ListTagsForStream", {"StreamName": stream_name})
    keys_after = {t["Key"] for t in after.get("Tags", [])}
    assert tag_key not in keys_after

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass