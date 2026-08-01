def test_put_record_happy_path(cli, kinesis, tmp_path):
    import time
    import json, time, base64, uuid

    stream_name = "test-put-record-" + uuid.uuid4().hex[:8]
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Poll until ACTIVE (read path requires populated shards)
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
    assert shard_id is not None, "stream never became ACTIVE with shards"

    payload = b"hello-kinesis-payload"
    data_b64 = base64.b64encode(payload).decode("ascii")
    partition_key = "pk-1"

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

    # Read the record back independently and assert round-trip Data + PartitionKey
    it_resp = kinesis.rpc("GetShardIterator", {
        "StreamName": stream_name,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    iterator = it_resp["ShardIterator"]

    found = None
    for _ in range(10):
        recs = kinesis.rpc("GetRecords", {"ShardIterator": iterator, "Limit": 100})
        for r in recs.get("Records", []):
            if r["PartitionKey"] == partition_key and r["Data"] == data_b64:
                found = r
                break
        if found:
            break
        iterator = recs["NextShardIterator"]
        time.sleep(0.2)

    assert found is not None, "put record not found via GetRecords"
    assert found["Data"] == data_b64
    assert found["PartitionKey"] == partition_key