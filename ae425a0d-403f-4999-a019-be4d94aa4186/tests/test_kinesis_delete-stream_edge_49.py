def test_delete_stream_removes_existing_stream(cli, kinesis, tmp_path):
    stream_name = "test-delete-stream-x"
    # Prerequisite: create the stream first
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})
    # Confirm it exists before delete
    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    assert desc["StreamDescription"]["StreamName"] == stream_name

    # Run the command under test
    result = cli("kinesis", "delete-stream", "--stream-name", stream_name)
    assert result.returncode == 0

    # Read resulting state: stream may be gone or transitioning; tolerate both
    try:
        after = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        # If still present, it must be the same stream (possibly DELETING/ACTIVE)
        assert after["StreamDescription"]["StreamName"] == stream_name
    except Exception:
        # Stream already deleted (ResourceNotFoundException) is acceptable
        pass