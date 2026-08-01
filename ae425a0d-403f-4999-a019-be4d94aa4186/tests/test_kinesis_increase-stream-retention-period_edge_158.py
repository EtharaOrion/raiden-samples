def test_increase_stream_retention_period_raises_retention(cli, kinesis):
    stream = "test-increase-retention-stream"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # default retention is 24; increase to 48
    result = cli(
        "kinesis",
        "increase-stream-retention-period",
        "--retention-period-hours",
        "48",
        "--stream-name",
        stream,
    )
    assert result.returncode == 0

    summary = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream})
    desc = summary["StreamDescriptionSummary"]
    assert desc["StreamName"] == stream
    assert desc["RetentionPeriodHours"] == 48

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass