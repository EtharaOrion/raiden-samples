def test_list_shards_returns_stream_shards(cli, kinesis, tmp_path):
    stream_name = "test-list-shards-happy"

    # Clean up any pre-existing stream
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Seed prerequisite state: create a stream
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 2})

    # Poll until ACTIVE so shards are populated
    import time
    active = False
    for _ in range(30):
        try:
            desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        except Exception:
            time.sleep(0.2)
            continue
        status = desc["StreamDescription"]["StreamStatus"]
        if status == "ACTIVE":
            active = True
            break
        time.sleep(0.5)
    assert active, "stream did not become ACTIVE"

    # Determine expected shard ids independently
    expected = kinesis.rpc("ListShards", {"StreamName": stream_name})
    expected_ids = sorted(s["ShardId"] for s in expected["Shards"])
    assert len(expected_ids) >= 1

    # Run the command under test
    result = cli("kinesis", "list-shards", "--stream-name", stream_name)
    assert result.returncode == 0

    import json
    payload = json.loads(result.stdout)
    got_ids = sorted(s["ShardId"] for s in payload["Shards"])
    assert got_ids == expected_ids

    # Cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass