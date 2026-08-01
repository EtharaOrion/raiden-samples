def test_list_streams_limit_out_of_range(cli, kinesis):
    result = cli("kinesis", "list-streams", "--limit", "10001")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "InvalidArgument" in result.stderr