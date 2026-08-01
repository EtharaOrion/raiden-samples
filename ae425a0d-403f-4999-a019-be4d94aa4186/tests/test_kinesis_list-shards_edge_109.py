def test_list_shards_returns_stream_shards(cli, kinesis, tmp_path):
    import time
    import json, time

    stream_name = "test-list-shards-stream-x"

    # Clean up any pre-existing stream to ensure isolation
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass
    time.sleep(0.2)

    # Seed prerequisite state: create the stream
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 2})

    # Poll until ACTIVE (read op requires ACTIVE stream with populated shards)
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

    # Run the command under test
    result = cli("kinesis", "list-shards", "--stream-name", stream_name)
    assert result.returncode == 0, result.stderr

    # Assert stdout structure
    out = json.loads(result.stdout)
    assert "Shards" in out
    cli_shard_ids = {s["ShardId"] for s in out["Shards"]}

    # Independent read via kinesis to verify effect/state
    rpc = kinesis.rpc("ListShards", {"StreamName": stream_name})
    rpc_shard_ids = {s["ShardId"] for s in rpc["Shards"]}

    assert len(rpc_shard_ids) == 2
    assert cli_shard_ids == rpc_shard_ids

    # Cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass