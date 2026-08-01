def test_increase_stream_retention_period_missing_required_arg(cli, kinesis, tmp_path):
    stream_name = "test-stream-missing-retention-arg"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})
    try:
        result = cli(
            "kinesis",
            "increase-stream-retention-period",
            "--stream-name",
            stream_name,
        )
        assert result.returncode != 0
        assert not result.stdout.strip(), result.stdout
        assert "argument" in result.stderr.lower() or "retention-period-hours" in result.stderr.lower()

        summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
        desc = summary["StreamDescriptionSummary"]
        assert desc["StreamName"] == stream_name
        assert desc["StreamStatus"] in ("CREATING", "ACTIVE")
        assert desc["RetentionPeriodHours"] == 24
    finally:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})