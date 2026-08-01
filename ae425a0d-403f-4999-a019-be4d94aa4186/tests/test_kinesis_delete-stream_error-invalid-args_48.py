def test_delete_stream_empty_stream_name_rejected(cli, kinesis):
    result = cli("kinesis", "delete-stream", "--stream-name", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "ValidationException" in result.stderr or "Invalid" in result.stderr