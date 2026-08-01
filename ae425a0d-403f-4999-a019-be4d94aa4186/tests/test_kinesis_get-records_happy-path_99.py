def test_get_records_happy_path_roundtrip(cli, kinesis, tmp_path):
    import time
    import json, base64, time

    stream = "test-getrecords-happy"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
    time.sleep(0.2)

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
    assert shard_id is not None, "stream did not become ACTIVE with shards"

    # Put a record
    payload = b"hello-world"
    data_b64 = base64.b64encode(payload).decode("ascii")
    part_key = "pk-1"
    kinesis.rpc("PutRecord", {
        "StreamName": stream,
        "Data": data_b64,
        "PartitionKey": part_key,
    })

    # Get a TRIM_HORIZON iterator to read from the start
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iterator = it["ShardIterator"]

    result = cli("kinesis", "get-records", "--shard-iterator", shard_iterator)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Records" in out
    assert isinstance(out["Records"], list)

    # If the CLI's first read returned no records (iterator lag), poll via rpc
    # using NextShardIterator to verify the round-trip effect independently.
    records = out["Records"]
    next_it = out.get("NextShardIterator")
    for _ in range(20):
        if records:
            break
        assert next_it is not None
        resp = kinesis.rpc("GetRecords", {"ShardIterator": next_it})
        records = resp.get("Records", [])
        next_it = resp.get("NextShardIterator")
        if not records:
            time.sleep(0.2)

    assert records, "expected to read back the put record"
    found = [r for r in records if r.get("PartitionKey") == part_key]
    assert found, "record with expected partition key not found"
    assert found[0]["Data"] == data_b64