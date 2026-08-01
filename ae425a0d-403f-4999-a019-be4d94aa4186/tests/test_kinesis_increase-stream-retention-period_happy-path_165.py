def test_increase_stream_retention_period_raises_retention(cli, kinesis):
    stream_name = "test-increase-retention-stream"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Verify the starting retention period (default 24)
    summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    start_hours = summary["StreamDescriptionSummary"]["RetentionPeriodHours"]
    assert start_hours == 24

    new_hours = 48
    result = cli(
        "kinesis",
        "increase-stream-retention-period",
        "--stream-name",
        stream_name,
        "--retention-period-hours",
        str(new_hours),
    )
    assert result.returncode == 0

    summary_after = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    assert (
        summary_after["StreamDescriptionSummary"]["RetentionPeriodHours"] == new_hours
    )

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})