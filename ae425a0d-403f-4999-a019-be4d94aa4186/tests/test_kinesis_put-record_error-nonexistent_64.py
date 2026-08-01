def test_put_record_nonexistent_stream(cli, kinesis):
    stream_name = "nonexistent-stream-put-record-xyz"

    # Ensure the stream does not exist
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Confirm absence via DescribeStream raising ResourceNotFoundException
    describe_failed = False
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    except Exception:
        describe_failed = True
    assert describe_failed

    result = cli(
        "kinesis", "put-record",
        "--stream-name", stream_name,
        "--data", "aGVsbG8=",
        "--partition-key", "pk-1",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Confirm the stream still does not exist
    still_absent = False
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    except Exception:
        still_absent = True
    assert still_absent