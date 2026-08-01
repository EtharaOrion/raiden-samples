def test_get_records_happy_path_roundtrip(cli, kinesis, tmp_path):
    import base64, json, time

    stream = "test-getrecords-happy"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Wait for ACTIVE so shards are populated
    deadline = time.time() + 20
    shard_id = None
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.5)
    assert shard_id is not None

    payload = b"hello-getrecords"
    data_b64 = base64.b64encode(payload).decode("ascii")
    pk = "partition-key-1"
    kinesis.rpc("PutRecord", {
        "StreamName": stream,
        "Data": data_b64,
        "PartitionKey": pk,
    })

    iter_resp = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iterator = iter_resp["ShardIterator"]

    result = cli("kinesis", "get-records", "--shard-iterator", shard_iterator)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    records = out.get("Records", [])
    assert any(
        r.get("PartitionKey") == pk and r.get("Data") == data_b64
        for r in records
    )

    # Independent verification of the same round trip via raw client
    iter_resp2 = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    got = kinesis.rpc("GetRecords", {"ShardIterator": iter_resp2["ShardIterator"]})
    assert any(
        r.get("PartitionKey") == pk and r.get("Data") == data_b64
        for r in got.get("Records", [])
    )

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass