def test_decrease_stream_retention_period_lowers_value(cli, kinesis):
    stream_name = "x" * 128
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})
    # Raise retention first so we have room to decrease
    kinesis.rpc("IncreaseStreamRetentionPeriod", {"StreamName": stream_name, "RetentionPeriodHours": 48})

    summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    assert summary["StreamDescriptionSummary"]["RetentionPeriodHours"] == 48

    result = cli(
        "kinesis", "decrease-stream-retention-period",
        "--retention-period-hours", "24",
        "--stream-name", stream_name,
    )
    assert result.returncode == 0

    summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    assert summary["StreamDescriptionSummary"]["StreamName"] == stream_name
    assert summary["StreamDescriptionSummary"]["RetentionPeriodHours"] == 24

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})