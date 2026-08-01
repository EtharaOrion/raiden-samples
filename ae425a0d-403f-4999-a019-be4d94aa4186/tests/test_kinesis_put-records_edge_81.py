def test_put_records_multiple_records_round_trip(cli, kinesis, tmp_path):
    import json, base64, time, uuid

    stream = "test-stream-" + uuid.uuid4().hex[:8]
    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Wait until ACTIVE so we can read back records
    deadline = time.time() + 10
    shard_id = None
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.3)
    assert shard_id is not None

    # Grab a TRIM_HORIZON iterator BEFORE putting records
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })["ShardIterator"]

    data1 = base64.b64encode(b"hello-one").decode()
    data2 = base64.b64encode(b"hello-two").decode()
    records = [
        {"Data": data1, "PartitionKey": "pk1"},
        {"Data": data2, "PartitionKey": "pk2"},
    ]
    records_file = tmp_path / "records.json"
    records_file.write_text(json.dumps(records))

    result = cli(
        "kinesis", "put-records",
        "--stream-name", stream,
        "--records", "file://" + str(records_file),
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["FailedRecordCount"] == 0
    assert len(out["Records"]) == len(records)

    # Read the records back via GetRecords and assert round-trip
    got_data = {}
    read_deadline = time.time() + 10
    while time.time() < read_deadline and len(got_data) < 2:
        resp = kinesis.rpc("GetRecords", {"ShardIterator": it, "Limit": 100})
        for r in resp.get("Records", []):
            got_data[r["PartitionKey"]] = r["Data"]
        it = resp["NextShardIterator"]
        if len(got_data) >= 2:
            break
        time.sleep(0.3)

    assert got_data.get("pk1") == data1
    assert got_data.get("pk2") == data2