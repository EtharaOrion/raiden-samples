def test_get_shard_iterator_trim_horizon(cli, kinesis, tmp_path):
    import json
    import time

    stream = "test-getsharditer-stream"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
    time.sleep(0.5)

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Poll until ACTIVE so shards are populated
    shard_id = None
    for _ in range(30):
        try:
            desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
        except Exception:
            time.sleep(0.2)
            continue
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.5)
    assert shard_id is not None, "stream did not become ACTIVE with shards"

    result = cli(
        "kinesis", "get-shard-iterator",
        "--stream-name", stream,
        "--shard-id", shard_id,
        "--shard-iterator-type", "TRIM_HORIZON",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    iterator = out["ShardIterator"]
    assert isinstance(iterator, str) and iterator

    # Independently verify the iterator works via GetRecords
    recs = kinesis.rpc("GetRecords", {"ShardIterator": iterator})
    assert "Records" in recs
    assert "NextShardIterator" in recs

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass