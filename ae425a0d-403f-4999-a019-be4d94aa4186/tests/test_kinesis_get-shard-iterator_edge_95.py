def test_get_shard_iterator_latest_returns_valid_iterator(cli, kinesis, tmp_path):
    import json
    import time

    stream = "test-getshiter-stream"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
    time.sleep(0.2)

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Poll until ACTIVE so shards are populated
    shard_id = None
    for _ in range(60):
        try:
            desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
        except Exception:
            time.sleep(0.2)
            continue
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd["Shards"]:
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.5)
    assert shard_id is not None, "stream never became ACTIVE with shards"

    result = cli(
        "kinesis", "get-shard-iterator",
        "--stream-name", stream,
        "--shard-id", shard_id,
        "--shard-iterator-type", "LATEST",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "ShardIterator" in out
    assert isinstance(out["ShardIterator"], str)
    assert out["ShardIterator"]

    # Independently confirm the iterator is usable against real state
    got = kinesis.rpc("GetRecords", {"ShardIterator": out["ShardIterator"]})
    assert "Records" in got
    assert "NextShardIterator" in got

    kinesis.rpc("DeleteStream", {"StreamName": stream})