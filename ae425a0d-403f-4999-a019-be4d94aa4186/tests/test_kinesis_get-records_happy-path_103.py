def test_get_records_happy_path_roundtrip(cli, kinesis, tmp_path):
    import time
    import json, base64, time

    stream = "test-getrecords-happy"
    # clean slate
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # poll until ACTIVE
    shard_id = None
    for _ in range(60):
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

    # put a record we can read back
    payload = b"hello-getrecords"
    data_b64 = base64.b64encode(payload).decode()
    partition_key = "pk-1"
    kinesis.rpc("PutRecord", {
        "StreamName": stream,
        "Data": data_b64,
        "PartitionKey": partition_key,
    })

    # get a TRIM_HORIZON iterator to read from the beginning
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iterator = it["ShardIterator"]

    # run command under test
    result = cli("kinesis", "get-records", "--shard-iterator", shard_iterator)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "Records" in out

    # the record we put must be readable back with same Data and PartitionKey
    records = out["Records"]
    # if this iterator batch didn't include it, follow NextShardIterator a few times
    found = any(r.get("Data") == data_b64 and r.get("PartitionKey") == partition_key
                for r in records)
    next_it = out.get("NextShardIterator")
    tries = 0
    while not found and next_it and tries < 10:
        more = kinesis.rpc("GetRecords", {"ShardIterator": next_it})
        for r in more.get("Records", []):
            if r.get("Data") == data_b64 and r.get("PartitionKey") == partition_key:
                found = True
                break
        next_it = more.get("NextShardIterator")
        tries += 1
        if not found:
            time.sleep(0.2)

    assert found, "record put was not read back via GetRecords roundtrip"