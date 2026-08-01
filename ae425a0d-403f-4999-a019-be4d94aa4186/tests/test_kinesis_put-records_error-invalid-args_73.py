def test_put_records_missing_required_records(cli, kinesis):
    stream = "test-put-records-missing-records"
    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})
    try:
        result = cli("kinesis", "put-records", "--stream-name", stream)
        assert result.returncode != 0
        assert not result.stdout.strip(), result.stdout
        assert "records" in result.stderr.lower()
    finally:
        kinesis.rpc("DeleteStream", {"StreamName": stream})