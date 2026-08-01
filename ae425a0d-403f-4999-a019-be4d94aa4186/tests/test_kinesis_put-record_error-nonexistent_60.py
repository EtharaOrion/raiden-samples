def test_put_record_error_nonexistent(cli, kinesis):
    stream_name = "nonexistent-stream-put-record-xyz"

    # Ensure the stream does not exist
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Confirm absence via DescribeStream raising ResourceNotFoundException
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        stream_exists = True
    except Exception:
        stream_exists = False
    assert not stream_exists

    import base64
    data_b64 = base64.b64encode(b"hello").decode()

    result = cli(
        "kinesis", "put-record",
        "--stream-name", stream_name,
        "--data", data_b64,
        "--partition-key", "pk-1",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # State assertion: stream still does not exist
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        still_exists = True
    except Exception:
        still_exists = False
    assert not still_exists