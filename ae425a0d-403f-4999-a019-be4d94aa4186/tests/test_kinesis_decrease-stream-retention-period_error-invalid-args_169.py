def test_decrease_stream_retention_period_missing_required_arg(cli, kinesis, tmp_path):
    stream_name = "test-decrease-retention-missing-arg"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})
    try:
        result = cli(
            "kinesis",
            "decrease-stream-retention-period",
            "--stream-name",
            stream_name,
        )
        assert result.returncode != 0
        assert not result.stdout.strip(), result.stdout
        assert "retention-period-hours" in result.stderr.lower() or "argument" in result.stderr.lower()

        # State unchanged: retention still at default
        summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
        desc = summary["StreamDescriptionSummary"]
        assert desc["StreamName"] == stream_name
        assert desc["StreamStatus"] in ("CREATING", "ACTIVE")
        assert desc["RetentionPeriodHours"] == 24
    finally:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})