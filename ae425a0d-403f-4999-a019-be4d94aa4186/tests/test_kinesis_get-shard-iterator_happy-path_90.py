def test_get_shard_iterator_happy_path(cli, kinesis, tmp_path):
    import json
    import time

    stream_name = "test-gsi-stream-happy"

    # Clean up any pre-existing stream
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Poll until ACTIVE so shards are populated
    deadline = time.time() + 30
    shard_id = None
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.5)

    assert shard_id is not None, "stream did not become ACTIVE with shards"

    result = cli(
        "kinesis", "get-shard-iterator",
        "--stream-name", stream_name,
        "--shard-id", shard_id,
        "--shard-iterator-type", "TRIM_HORIZON",
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "ShardIterator" in out
    assert isinstance(out["ShardIterator"], str)
    assert out["ShardIterator"]

    # Independently verify the iterator is usable via GetRecords
    got = kinesis.rpc("GetRecords", {"ShardIterator": out["ShardIterator"]})
    assert "Records" in got
    assert "NextShardIterator" in got

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})