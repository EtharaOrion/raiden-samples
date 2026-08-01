def test_list_shards_happy_path(cli, kinesis, tmp_path):
    import json
    import time

    stream_name = "test-list-shards-happy"

    # Seed prerequisite state: create the stream
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 2})

    # Poll until ACTIVE so shards are populated
    deadline = time.time() + 30
    shards_from_rpc = []
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        status = desc["StreamDescription"]["StreamStatus"]
        if status == "ACTIVE":
            shards_from_rpc = desc["StreamDescription"]["Shards"]
            if shards_from_rpc:
                break
        time.sleep(0.5)

    assert shards_from_rpc, "stream never became ACTIVE with shards"
    expected_shard_ids = {s["ShardId"] for s in shards_from_rpc}

    # Run the command under test
    result = cli("kinesis", "list-shards", "--stream-name", stream_name)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Shards" in out
    listed_ids = {s["ShardId"] for s in out["Shards"]}
    assert listed_ids == expected_shard_ids

    # Independent read-back via kinesis RPC confirms the same shards exist
    ls = kinesis.rpc("ListShards", {"StreamName": stream_name})
    rpc_ids = {s["ShardId"] for s in ls["Shards"]}
    assert expected_shard_ids <= rpc_ids

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})