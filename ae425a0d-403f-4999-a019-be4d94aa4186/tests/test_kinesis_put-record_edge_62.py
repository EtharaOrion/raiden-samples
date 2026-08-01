def test_put_record_roundtrip_data_readback(cli, kinesis):
    import time
    import json, base64, time, uuid

    stream_name = "test-put-record-" + uuid.uuid4().hex[:12]
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Wait for ACTIVE so shards are populated for the read path
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
    assert shard_id is not None

    try:
        payload = b"hello-kinesis-payload"
        data_b64 = base64.b64encode(payload).decode()
        partition_key = "pk-1234"

        result = cli(
            "kinesis", "put-record",
            "--data", data_b64,
            "--partition-key", partition_key,
            "--stream-name", stream_name,
        )
        assert result.returncode == 0, result.stderr

        out = json.loads(result.stdout)
        assert "ShardId" in out
        assert "SequenceNumber" in out

        # Read back via GetShardIterator + GetRecords
        it = kinesis.rpc("GetShardIterator", {
            "StreamName": stream_name,
            "ShardId": shard_id,
            "ShardIteratorType": "TRIM_HORIZON",
        })
        iterator = it["ShardIterator"]

        found = None
        for _ in range(20):
            recs = kinesis.rpc("GetRecords", {"ShardIterator": iterator, "Limit": 100})
            for r in recs.get("Records", []):
                if r["PartitionKey"] == partition_key and r["Data"] == data_b64:
                    found = r
                    break
            if found:
                break
            iterator = recs["NextShardIterator"]
            time.sleep(0.2)

        assert found is not None
        assert found["Data"] == data_b64
        assert found["PartitionKey"] == partition_key
    finally:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})