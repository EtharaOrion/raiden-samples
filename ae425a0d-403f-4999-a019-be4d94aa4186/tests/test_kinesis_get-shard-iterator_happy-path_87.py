def test_get_shard_iterator_happy_path(cli, kinesis, tmp_path):
    import json
    import time

    stream_name = "test-gsi-stream-happy"

    # Clean up any pre-existing stream
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass
    time.sleep(0.2)

    # Seed prerequisite state: create a stream
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Poll until ACTIVE so shards are populated
    shard_id = None
    for _ in range(50):
        try:
            desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        except Exception:
            time.sleep(0.2)
            continue
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.2)

    assert shard_id is not None, "stream never became ACTIVE with shards"

    # Run the command under test
    result = cli(
        "kinesis", "get-shard-iterator",
        "--stream-name", stream_name,
        "--shard-id", shard_id,
        "--shard-iterator-type", "TRIM_HORIZON",
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    iterator = out["ShardIterator"]
    assert isinstance(iterator, str) and iterator

    # Assert the iterator actually works against real kinesis state:
    # use it to read records (round-trip via the raw client).
    recs = kinesis.rpc("GetRecords", {"ShardIterator": iterator})
    assert "Records" in recs
    assert "NextShardIterator" in recs