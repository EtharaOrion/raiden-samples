def test_put_records_happy_path(cli, kinesis, tmp_path):
    import time
    import json, base64, time

    stream_name = "test-put-records-stream"

    # cleanup any pre-existing state
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # poll until ACTIVE so shards are populated for the read path
    shard_id = None
    for _ in range(30):
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

    data1 = base64.b64encode(b"hello-record-one").decode()
    data2 = base64.b64encode(b"hello-record-two").decode()
    records = [
        {"Data": data1, "PartitionKey": "pk-1"},
        {"Data": data2, "PartitionKey": "pk-2"},
    ]

    result = cli(
        "kinesis", "put-records",
        "--stream-name", stream_name,
        "--records", json.dumps(records),
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["FailedRecordCount"] == 0
    assert len(out["Records"]) == len(records)

    # independent read-back via GetRecords round trip
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream_name,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iter = it["ShardIterator"]

    seen = {}
    for _ in range(10):
        gr = kinesis.rpc("GetRecords", {"ShardIterator": shard_iter, "Limit": 100})
        for rec in gr.get("Records", []):
            seen[rec["PartitionKey"]] = rec["Data"]
        shard_iter = gr["NextShardIterator"]
        if len(seen) >= len(records):
            break
        time.sleep(0.2)

    assert seen.get("pk-1") == data1
    assert seen.get("pk-2") == data2

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})