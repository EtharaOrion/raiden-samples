def test_add_tags_to_stream_invalid_args(cli, kinesis, tmp_path):
    stream_name = "test-invalid-args-stream"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli(
        "kinesis", "add-tags-to-stream",
        "--stream-name", stream_name,
        "--tags", '{"env":"prod"}',
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    # The tag should NOT have been applied since the command failed on arg parsing
    tags_resp = kinesis.rpc("ListTagsForStream", {"StreamName": stream_name})
    keys = {t["Key"] for t in tags_resp.get("Tags", [])}
    assert "env" not in keys