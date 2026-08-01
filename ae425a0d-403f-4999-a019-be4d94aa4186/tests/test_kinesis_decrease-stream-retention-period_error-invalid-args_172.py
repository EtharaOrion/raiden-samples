def test_decrease_stream_retention_period_invalid_flag(cli, kinesis):
    stream_name = "test-decrease-retention-invalid-flag"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})
    try:
        result = cli(
            "kinesis",
            "decrease-stream-retention-period",
            "--stream-name",
            stream_name,
            "--retention-period-hours",
            "24",
            "--not-a-real-flag",
            "x",
        )
        assert result.returncode != 0
        assert not result.stdout.strip(), result.stdout
        assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr
    finally:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})