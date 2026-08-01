def test_list_streams_with_limit(cli, kinesis):
    stream_name = "test-list-limit-stream"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Confirm the stream exists in the backend independently.
    all_streams = kinesis.rpc("ListStreams", {})
    assert stream_name in all_streams.get("StreamNames", [])

    result = cli("kinesis", "list-streams", "--limit", "1")
    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    assert "StreamNames" in parsed
    assert isinstance(parsed["StreamNames"], list)
    assert len(parsed["StreamNames"]) <= 1

    # Independent read-back through the raw client confirms our stream is present.
    reread = kinesis.rpc("ListStreams", {})
    assert stream_name in reread.get("StreamNames", [])

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass