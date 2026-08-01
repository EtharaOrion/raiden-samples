def test_create_stream_missing_required_stream_name(cli, kinesis):
    result = cli("kinesis", "create-stream", "--shard-count", "1")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "stream-name" in result.stderr.lower() or "streamname" in result.stderr.lower()