def test_create_stream_happy_path(cli, kinesis):
    stream_name = "test-create-stream-happy-v3"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    existing = kinesis.rpc("ListStreams", {})
    assert stream_name not in existing.get("StreamNames", [])

    result = cli("kinesis", "create-stream", "--stream-name", stream_name,
                 "--shard-count", "1")
    assert result.returncode == 0

    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    sd = desc["StreamDescription"]
    assert sd["StreamName"] == stream_name
    assert sd["StreamStatus"] in ("CREATING", "ACTIVE")

    listed = kinesis.rpc("ListStreams", {})
    assert stream_name in listed.get("StreamNames", [])

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass