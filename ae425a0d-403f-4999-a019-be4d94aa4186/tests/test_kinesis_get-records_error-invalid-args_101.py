def test_get_records_invalid_args(cli, kinesis):
    result = cli("kinesis", "get-records", "--shard-iterator", "someiterator",
                 "--not-a-real-flag", "x")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr.lower() or "unknown" in result.stderr.lower() \
        or "usage" in result.stderr.lower() or "argument" in result.stderr.lower()