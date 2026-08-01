def test_list_streams_happy_path(cli, kinesis, tmp_path):
    import json
    stream_name = "test-list-streams-happy-" + tmp_path.name.replace("_", "-")
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # confirm the seeded stream exists in kinesis state
    seeded = kinesis.rpc("ListStreams", {})
    assert stream_name in seeded["StreamNames"]

    result = cli("kinesis", "list-streams")
    assert result.returncode == 0

    parsed = json.loads(result.stdout)
    assert "StreamNames" in parsed
    assert isinstance(parsed["StreamNames"], list)
    assert stream_name in parsed["StreamNames"]

    # independent read-back through kinesis
    after = kinesis.rpc("ListStreams", {})
    assert stream_name in after["StreamNames"]

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})