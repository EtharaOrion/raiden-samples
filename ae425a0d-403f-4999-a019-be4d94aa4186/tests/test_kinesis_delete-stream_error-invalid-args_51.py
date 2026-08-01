def test_delete_stream_invalid_name_too_long(cli, kinesis):
    long_name = "x" * 123
    result = cli("kinesis", "delete-stream", "--stream-name", long_name)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "ValidationException" in result.stderr