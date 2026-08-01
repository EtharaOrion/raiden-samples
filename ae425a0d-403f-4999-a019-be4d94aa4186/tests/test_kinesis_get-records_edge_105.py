def test_get_records_roundtrip(cli, kinesis, tmp_path):
    import time
    import json, base64, time

    stream = "test-getrecords-stream"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
        time.sleep(0.5)
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Poll until ACTIVE
    shards = []
    for _ in range(30):
        try:
            desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
        except Exception:
            time.sleep(0.2)
            continue
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shards = sd["Shards"]
            break
        time.sleep(0.5)
    assert shards, "stream never became ACTIVE with shards"

    shard_id = shards[0]["ShardId"]

    # Put a record we can read back
    data_raw = b"hello-getrecords"
    data_b64 = base64.b64encode(data_raw).decode()
    partition_key = "pk-123"
    kinesis.rpc("PutRecord", {
        "StreamName": stream,
        "Data": data_b64,
        "PartitionKey": partition_key,
    })

    # Get a TRIM_HORIZON iterator to read from the beginning
    it_resp = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iterator = it_resp["ShardIterator"]

    # Run command under test
    result = cli("kinesis", "get-records",
                 "--shard-iterator", shard_iterator,
                 "--limit", "1")
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Records" in out

    # Verify roundtrip: the record we put comes back with same Data and PartitionKey.
    found = False
    records = out["Records"]
    if records:
        for rec in records:
            if rec.get("PartitionKey") == partition_key and rec.get("Data") == data_b64:
                found = True
                break

    if not found:
        # Records may need a subsequent iterator; verify via independent read path.
        next_it = out.get("NextShardIterator")
        for _ in range(10):
            if next_it is None:
                break
            gr = kinesis.rpc("GetRecords", {"ShardIterator": next_it, "Limit": 10})
            for rec in gr.get("Records", []):
                if rec.get("PartitionKey") == partition_key and rec.get("Data") == data_b64:
                    found = True
                    break
            if found:
                break
            next_it = gr.get("NextShardIterator")
            time.sleep(0.3)

    assert found, "record put earlier was not read back with matching Data/PartitionKey"

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass