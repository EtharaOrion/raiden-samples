def test_describe_stream_returns_stream_description(cli, kinesis):
    stream_name = "test-describe-stream-edge"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli("kinesis", "describe-stream", "--stream-name", stream_name)
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    assert "StreamDescription" in parsed
    assert parsed["StreamDescription"]["StreamName"] == stream_name

    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    assert desc["StreamDescription"]["StreamName"] == stream_name
    assert desc["StreamDescription"]["StreamStatus"] in ("CREATING", "ACTIVE")

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass