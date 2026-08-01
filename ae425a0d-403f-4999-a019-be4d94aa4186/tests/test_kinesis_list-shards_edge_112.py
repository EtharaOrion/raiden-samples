def test_list_shards_happy_path(cli, kinesis):
    stream_name = "x" * 123
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Poll until ACTIVE so shards are populated
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
    assert active, "stream never became ACTIVE"

    expected_shard_ids = {
        s["ShardId"] for s in desc["StreamDescription"]["Shards"]
    }
    assert expected_shard_ids

    try:
        result = cli("kinesis", "list-shards", "--stream-name", stream_name)
        assert result.returncode == 0, result.stderr

        out = json.loads(result.stdout)
        cli_shard_ids = {s["ShardId"] for s in out["Shards"]}
        assert cli_shard_ids == expected_shard_ids

        # Independent state read via raw HTTP client
        listed = kinesis.rpc("ListShards", {"StreamName": stream_name})
        state_shard_ids = {s["ShardId"] for s in listed["Shards"]}
        assert state_shard_ids == expected_shard_ids
    finally:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})


import json
import time