def test_list_shards_happy_path(cli, kinesis, tmp_path):
    import json
    import time

    stream_name = "test-list-shards-happy"

    # Clean up any prior state
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Seed prerequisite state: create a stream
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 2})

    # Poll until ACTIVE (read path requires an ACTIVE stream with populated Shards)
    deadline = time.time() + 30
    shards = []
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd["Shards"]:
            shards = sd["Shards"]
            break
        time.sleep(0.5)

    assert shards, "stream never became ACTIVE with populated shards"
    expected_shard_ids = {s["ShardId"] for s in shards}

    # Run the command under test
    result = cli("kinesis", "list-shards", "--stream-name", stream_name)
    assert result.returncode == 0, result.stderr

    # Parse stdout structure
    out = json.loads(result.stdout)
    assert "Shards" in out
    listed_ids = {s["ShardId"] for s in out["Shards"]}
    assert listed_ids == expected_shard_ids

    # Independent read-back via kinesis to assert resulting state
    rpc_out = kinesis.rpc("ListShards", {"StreamName": stream_name})
    rpc_ids = {s["ShardId"] for s in rpc_out["Shards"]}
    assert rpc_ids == expected_shard_ids

    # Cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass