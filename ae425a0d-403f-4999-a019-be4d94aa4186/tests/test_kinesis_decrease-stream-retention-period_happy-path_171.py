def test_decrease_stream_retention_period_happy_path(cli, kinesis):
    stream = "test-decrease-retention-stream"
    # Clean slate
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass

    # Seed: create stream
    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Raise retention above the minimum so we have room to decrease
    kinesis.rpc("IncreaseStreamRetentionPeriod", {
        "StreamName": stream,
        "RetentionPeriodHours": 48,
    })

    # Confirm the seeded value
    before = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream})
    assert before["StreamDescriptionSummary"]["RetentionPeriodHours"] == 48

    # Run command under test: decrease to 24
    result = cli(
        "kinesis", "decrease-stream-retention-period",
        "--stream-name", stream,
        "--retention-period-hours", "24",
    )
    assert result.returncode == 0

    # Assert resulting state via independent read
    after = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream})
    summary = after["StreamDescriptionSummary"]
    assert summary["StreamName"] == stream
    assert summary["RetentionPeriodHours"] == 24

    # Cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass