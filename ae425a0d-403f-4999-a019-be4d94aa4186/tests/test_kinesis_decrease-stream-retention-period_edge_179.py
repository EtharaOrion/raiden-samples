def test_decrease_stream_retention_period_lowers_value(cli, kinesis):
    stream = "test-decrease-retention-stream"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Raise retention first so we have room to decrease
    kinesis.rpc("IncreaseStreamRetentionPeriod", {"StreamName": stream, "RetentionPeriodHours": 48})

    summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream})
    start_hours = summary["StreamDescriptionSummary"]["RetentionPeriodHours"]
    assert start_hours == 48

    result = cli(
        "kinesis",
        "decrease-stream-retention-period",
        "--stream-name",
        stream,
        "--retention-period-hours",
        "24",
    )
    assert result.returncode == 0, result.stderr

    summary_after = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream})
    new_hours = summary_after["StreamDescriptionSummary"]["RetentionPeriodHours"]
    assert new_hours == 24
    assert new_hours < start_hours

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass