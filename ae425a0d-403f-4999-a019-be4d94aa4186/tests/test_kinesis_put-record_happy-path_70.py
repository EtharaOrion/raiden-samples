def test_put_record_happy_path(cli, kinesis, tmp_path):
    import time
    import json, base64, time, uuid

    stream_name = "test-put-record-" + uuid.uuid4().hex[:12]
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Wait for stream to become ACTIVE so we can read records back
    shard_id = None
    for _ in range(60):
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
    assert shard_id is not None, "stream did not become ACTIVE"

    payload = b"hello-kinesis-payload"
    data_b64 = base64.b64encode(payload).decode("ascii")
    partition_key = "pk-" + uuid.uuid4().hex[:8]

    result = cli(
        "kinesis", "put-record",
        "--stream-name", stream_name,
        "--data", data_b64,
        "--partition-key", partition_key,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "ShardId" in out
    assert "SequenceNumber" in out

    # Read the record back through GetRecords and verify round trip
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream_name,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iter = it["ShardIterator"]

    found = None
    for _ in range(20):
        recs = kinesis.rpc("GetRecords", {"ShardIterator": shard_iter, "Limit": 100})
        for r in recs.get("Records", []):
            if r["PartitionKey"] == partition_key:
                found = r
                break
        if found is not None:
            break
        shard_iter = recs["NextShardIterator"]
        time.sleep(0.2)

    assert found is not None, "put record not read back"
    assert found["Data"] == data_b64
    assert found["PartitionKey"] == partition_key

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})