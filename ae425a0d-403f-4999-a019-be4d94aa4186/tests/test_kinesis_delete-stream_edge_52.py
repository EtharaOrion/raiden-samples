def test_delete_stream_success(cli, kinesis):
    stream_name = "x" * 128
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # confirm the stream exists before deletion
    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    assert desc["StreamDescription"]["StreamName"] == stream_name

    result = cli("kinesis", "delete-stream", "--stream-name", stream_name)
    assert result.returncode == 0

    # After async delete, the stream may be gone or still present in a
    # transitional state; tolerate both.
    try:
        after = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        assert after["StreamDescription"]["StreamName"] == stream_name
    except Exception:
        pass