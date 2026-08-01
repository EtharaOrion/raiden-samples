def test_describe_stream_happy_path(cli, kinesis, tmp_path):
    stream_name = "test-describe-stream-hp"
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
    sd = desc["StreamDescription"]
    assert sd["StreamName"] == stream_name
    assert sd["StreamStatus"] in ("CREATING", "ACTIVE")

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass