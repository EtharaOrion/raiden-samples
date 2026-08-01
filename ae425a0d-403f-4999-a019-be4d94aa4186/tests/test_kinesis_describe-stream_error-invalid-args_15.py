def test_describe_stream_invalid_stream_name_too_long(cli, kinesis):
    bad_name = "x" * 129
    result = cli("kinesis", "describe-stream", "--stream-name", bad_name)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "ValidationError" in result.stderr
    # confirm no such stream exists in the backend
    listed = kinesis.rpc("ListStreams", {})
    assert bad_name not in listed.get("StreamNames", [])