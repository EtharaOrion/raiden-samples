def test_describe_stream_long_name(cli, kinesis):
    stream_name = "x" * 120
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli("kinesis", "describe-stream", "--stream-name", stream_name)
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    desc = payload["StreamDescription"]
    assert desc["StreamName"] == stream_name
    assert desc["StreamStatus"] in ("CREATING", "ACTIVE")

    described = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    assert described["StreamDescription"]["StreamName"] == stream_name

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})