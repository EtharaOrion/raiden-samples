def test_add_tags_to_stream_happy_path(cli, kinesis):
    stream_name = "test-add-tags-happy-stream"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli(
        "kinesis", "add-tags-to-stream",
        "--stream-name", stream_name,
        "--tags", '{"env":"prod","team":"data"}',
    )
    assert result.returncode == 0

    resp = kinesis.rpc("ListTagsForStream", {"StreamName": stream_name})
    tags = {t["Key"]: t["Value"] for t in resp.get("Tags", [])}
    assert tags.get("env") == "prod"
    assert tags.get("team") == "data"

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass