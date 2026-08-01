def test_add_tags_to_stream_invalid_args(cli, kinesis, tmp_path):
    stream_name = "test-invalid-args-stream"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli(
        "kinesis", "add-tags-to-stream",
        "--stream-name", stream_name,
        "--tags", '{"env":"prod"}',
        "--attribute-definitions", "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "argument" in result.stderr.lower()

    # The invalid invocation must not have applied the tag.
    tags_resp = kinesis.rpc("ListTagsForStream", {"StreamName": stream_name})
    keys = [t["Key"] for t in tags_resp.get("Tags", [])]
    assert "env" not in keys