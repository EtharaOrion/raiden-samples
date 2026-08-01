def test_create_stream_creates_observable_stream(cli, kinesis, tmp_path):
    stream_name = "test-create-stream-edge-happy"
    existing = kinesis.rpc("ListStreams", {}).get("StreamNames", [])
    if stream_name in existing:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})

    result = cli("kinesis", "create-stream", "--stream-name", stream_name,
                 "--shard-count", "1")
    assert result.returncode == 0

    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    sd = desc["StreamDescription"]
    assert sd["StreamName"] == stream_name
    assert sd["StreamStatus"] in ("CREATING", "ACTIVE")

    names = kinesis.rpc("ListStreams", {}).get("StreamNames", [])
    assert stream_name in names

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})