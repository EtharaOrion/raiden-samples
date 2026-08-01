def test_list_shards_happy_path(cli, kinesis, tmp_path):
    import json
    import time

    stream_name = "test-list-shards-stream"

    # Clean up any prior state
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Seed prerequisite state: create a stream
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 2})

    # Poll until ACTIVE so shards are populated (read path requirement)
    deadline = time.time() + 20
    status = None
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        status = desc["StreamDescription"]["StreamStatus"]
        if status == "ACTIVE":
            break
        time.sleep(0.5)
    assert status == "ACTIVE"

    # Run the command under test
    result = cli("kinesis", "list-shards", "--stream-name", stream_name)
    assert result.returncode == 0, result.stderr

    # Parse stdout structure
    out = json.loads(result.stdout)
    assert "Shards" in out
    cli_shard_ids = sorted(s["ShardId"] for s in out["Shards"])
    assert len(cli_shard_ids) > 0

    # Independent read via raw kinesis rpc to confirm the resulting state
    listed = kinesis.rpc("ListShards", {"StreamName": stream_name})
    state_shard_ids = sorted(s["ShardId"] for s in listed["Shards"])
    assert state_shard_ids == cli_shard_ids

    # Cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass