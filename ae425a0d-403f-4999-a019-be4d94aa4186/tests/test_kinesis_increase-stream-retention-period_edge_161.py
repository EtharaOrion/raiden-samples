def test_increase_stream_retention_period_raises_value(cli, kinesis):
    stream_name = "test-increase-retention-stream-edge"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    current = summary["StreamDescriptionSummary"]["RetentionPeriodHours"]

    new_value = current + 48

    result = cli(
        "kinesis",
        "increase-stream-retention-period",
        "--retention-period-hours",
        str(new_value),
        "--stream-name",
        stream_name,
    )

    assert result.returncode == 0

    after = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    assert after["StreamDescriptionSummary"]["RetentionPeriodHours"] == new_value

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass