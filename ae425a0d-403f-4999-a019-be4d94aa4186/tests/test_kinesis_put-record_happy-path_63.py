def test_put_record_happy_path_round_trip(cli, kinesis, tmp_path):
    import time
    import json, base64, time

    stream = "test-put-record-happy-" + str(int(time.time() * 1000))
    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Wait for ACTIVE so shards are populated for read-back
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
        time.sleep(0.2)
    assert shard_id is not None, "stream did not become ACTIVE with shards"

    payload = b"hello-kinesis-happy-path"
    data_b64 = base64.b64encode(payload).decode("ascii")
    partition_key = "pk-happy-1"

    result = cli(
        "kinesis", "put-record",
        "--stream-name", stream,
        "--data", data_b64,
        "--partition-key", partition_key,
    )

    assert result.returncode == 0, result.stderr
    out = json.loads(result.stdout)
    assert "ShardId" in out
    assert "SequenceNumber" in out

    # Read back the record via GetShardIterator + GetRecords
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iterator = it["ShardIterator"]

    found = None
    for _ in range(10):
        recs = kinesis.rpc("GetRecords", {"ShardIterator": shard_iterator, "Limit": 100})
        for r in recs.get("Records", []):
            if r["PartitionKey"] == partition_key:
                found = r
                break
        if found:
            break
        shard_iterator = recs["NextShardIterator"]
        time.sleep(0.2)

    assert found is not None, "put record not found on read-back"
    assert found["PartitionKey"] == partition_key
    assert found["Data"] == data_b64

    kinesis.rpc("DeleteStream", {"StreamName": stream})