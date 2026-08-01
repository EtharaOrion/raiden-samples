def test_decrease_stream_retention_period_nonexistent(cli, kinesis):
    stream_name = "nonexistent-stream-xyz-123"

    # Ensure the stream does not exist
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Confirm absence
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        exists = True
    except Exception:
        exists = False
    assert not exists, "precondition failed: stream should not exist"

    result = cli(
        "kinesis",
        "decrease-stream-retention-period",
        "--stream-name",
        stream_name,
        "--retention-period-hours",
        "24",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr