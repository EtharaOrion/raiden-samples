def test_get_records_roundtrip(cli, kinesis, tmp_path):
    import time
    import json, base64, time

    stream = "test-get-records-roundtrip"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Poll until ACTIVE
    shard_id = None
    for _ in range(50):
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
    assert shard_id is not None

    # Put a record so there's something to read back
    payload = b"hello-world"
    data_b64 = base64.b64encode(payload).decode("ascii")
    part_key = "pk-1"
    kinesis.rpc("PutRecord", {
        "StreamName": stream,
        "Data": data_b64,
        "PartitionKey": part_key,
    })

    # Get a TRIM_HORIZON iterator to read from start
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iter = it["ShardIterator"]

    # Run the candidate CLI
    result = cli("kinesis", "get-records", "--shard-iterator", shard_iter)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Records" in out

    # The round-trip: our put record must be readable with same Data & PartitionKey.
    # If not returned immediately, poll via NextShardIterator.
    found = None
    records = out["Records"]
    next_iter = out.get("NextShardIterator")
    tries = 0
    while found is None and tries < 20:
        for rec in records:
            if rec["PartitionKey"] == part_key and rec["Data"] == data_b64:
                found = rec
                break
        if found is not None or not next_iter:
            break
        resp = kinesis.rpc("GetRecords", {"ShardIterator": next_iter})
        records = resp["Records"]
        next_iter = resp.get("NextShardIterator")
        tries += 1
        time.sleep(0.2)

    assert found is not None
    assert found["Data"] == data_b64
    assert found["PartitionKey"] == part_key

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass