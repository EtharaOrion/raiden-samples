def test_put_record_roundtrip_active_stream(cli, kinesis, tmp_path):
    import time
    import json, base64, time

    stream = "test-putrecord-roundtrip-stream"

    # Clean up any pre-existing stream, then create fresh
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Poll until ACTIVE (required for read path)
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
    assert shard_id is not None, "stream never became ACTIVE with shards"

    partition_key = "pk-edgecase"
    raw = b"hello-edge-record"
    data_b64 = base64.b64encode(raw).decode("ascii")

    # Run command under test
    result = cli(
        "kinesis", "put-record",
        "--data", data_b64,
        "--partition-key", partition_key,
        "--stream-name", stream,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "ShardId" in out
    assert "SequenceNumber" in out

    # Independent read-back: GetShardIterator + GetRecords
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iter = it["ShardIterator"]

    found = None
    for _ in range(10):
        recs = kinesis.rpc("GetRecords", {"ShardIterator": shard_iter, "Limit": 100})
        for r in recs.get("Records", []):
            if r["PartitionKey"] == partition_key and r["Data"] == data_b64:
                found = r
                break
        if found is not None:
            break
        shard_iter = recs["NextShardIterator"]
        time.sleep(0.3)

    assert found is not None, "put record was not readable back"
    assert found["Data"] == data_b64
    assert found["PartitionKey"] == partition_key