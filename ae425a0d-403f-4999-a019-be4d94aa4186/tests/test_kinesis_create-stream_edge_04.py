def test_create_stream_max_length_name(cli, kinesis):
    stream_name = "x" * 128
    # ensure clean slate
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    result = cli("kinesis", "create-stream", "--stream-name", stream_name, "--shard-count", "1")
    assert result.returncode == 0

    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    sd = desc["StreamDescription"]
    assert sd["StreamName"] == stream_name
    assert sd["StreamStatus"] in ("CREATING", "ACTIVE")

    # cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass