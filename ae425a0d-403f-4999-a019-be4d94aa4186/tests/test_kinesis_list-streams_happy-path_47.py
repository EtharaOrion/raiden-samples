def test_list_streams_shows_created_stream(cli, kinesis):
    stream_name = "test-list-streams-happy"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    assert desc["StreamDescription"]["StreamName"] == stream_name

    result = cli("kinesis", "list-streams")
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    assert isinstance(payload.get("StreamNames"), list)
    assert stream_name in payload["StreamNames"]

    listed = kinesis.rpc("ListStreams", {})
    assert stream_name in listed["StreamNames"]

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass