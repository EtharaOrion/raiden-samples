def test_add_tags_to_stream_missing_required_tags(cli, kinesis):
    stream_name = "test-add-tags-missing-tags-stream"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli("kinesis", "add-tags-to-stream", "--stream-name", stream_name)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Tags" in result.stderr or "tags" in result.stderr

    # State assertion: no tags were added since the call must fail
    tags_resp = kinesis.rpc("ListTagsForStream", {"StreamName": stream_name})
    assert tags_resp.get("Tags", []) == []

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})