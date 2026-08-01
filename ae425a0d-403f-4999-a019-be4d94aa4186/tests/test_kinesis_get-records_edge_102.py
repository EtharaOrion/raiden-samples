def test_get_records_round_trip_returns_put_record(cli, kinesis, tmp_path):
    import json, base64, time

    stream = "test-getrec-rt-stream"
    # clean up any prior state
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass

    # seed prerequisite state FIRST
    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # poll until ACTIVE (read ops require an ACTIVE stream with populated shards)
    shard_id = None
    deadline = time.time() + 30
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.5)
    assert shard_id is not None, "stream did not become ACTIVE with shards"

    # put a record we can read back
    payload = b"hello-get-records-edge"
    data_b64 = base64.b64encode(payload).decode("ascii")
    partition_key = "pk-edge-1"
    kinesis.rpc("PutRecord", {
        "StreamName": stream,
        "Data": data_b64,
        "PartitionKey": partition_key,
    })

    # obtain a real shard iterator from TRIM_HORIZON
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iterator = it["ShardIterator"]

    # run the command under test with a VALID iterator
    result = cli("kinesis", "get-records", "--shard-iterator", shard_iterator)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    records = out.get("Records", [])

    # GetRecords may need a follow-up iterator hop on some backends; retry a bit
    deadline = time.time() + 15
    while not records and time.time() < deadline:
        nxt = out.get("NextShardIterator")
        if not nxt:
            break
        result = cli("kinesis", "get-records", "--shard-iterator", nxt)
        assert result.returncode == 0, result.stderr
        out = json.loads(result.stdout)
        records = out.get("Records", [])
        if not records:
            time.sleep(0.5)

    assert records, "expected at least one record from get-records round trip"

    # assert the ROUND TRIP: same base64 Data and PartitionKey we put
    matched = [r for r in records if r.get("PartitionKey") == partition_key]
    assert matched, "put PartitionKey not found in get-records output"
    assert any(r.get("Data") == data_b64 for r in matched), \
        "put Data blob not round-tripped through get-records"