def test_increase_stream_retention_period_invalid_args(cli, kinesis):
    stream_name = "test-invalid-flag-stream"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli(
        "kinesis",
        "increase-stream-retention-period",
        "--stream-name",
        stream_name,
        "--retention-period-hours",
        "48",
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown options" in result.stderr

    summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    desc = summary["StreamDescriptionSummary"]
    assert desc["StreamName"] == stream_name
    assert desc["RetentionPeriodHours"] == 24