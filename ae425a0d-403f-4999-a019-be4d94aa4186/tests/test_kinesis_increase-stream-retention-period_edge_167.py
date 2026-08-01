def test_increase_stream_retention_period_raises_value(cli, kinesis):
    stream = "test-increase-retention-stream"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream})
    current = summary["StreamDescriptionSummary"]["RetentionPeriodHours"]

    new_value = current + 24

    result = cli(
        "kinesis",
        "increase-stream-retention-period",
        "--stream-name",
        stream,
        "--retention-period-hours",
        str(new_value),
    )
    assert result.returncode == 0

    after = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream})
    assert after["StreamDescriptionSummary"]["RetentionPeriodHours"] == new_value

    kinesis.rpc("DeleteStream", {"StreamName": stream})