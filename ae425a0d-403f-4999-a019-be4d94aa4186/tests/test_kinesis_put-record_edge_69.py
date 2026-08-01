def test_put_record_empty_data_edge(cli, kinesis, tmp_path):
    import time
    import json, time, base64

    stream_name = "test-put-record-empty-data-edge"

    # Clean up any pre-existing stream from a prior run
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Seed prerequisite state: create the stream
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Poll until ACTIVE so the read path is available
    for _ in range(30):
        try:
            desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        except Exception:
            time.sleep(0.2)
            continue
        status = desc["StreamDescription"]["StreamStatus"]
        if status == "ACTIVE":
            break
        time.sleep(0.5)
    else:
        raise AssertionError("stream did not become ACTIVE")

    partition_key = "pk-empty-data"

    # Run the command under test: put a record with EMPTY data
    result = cli(
        "kinesis", "put-record",
        "--stream-name", stream_name,
        "--data", "",
        "--partition-key", partition_key,
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "ShardId" in out
    assert "SequenceNumber" in out

    # Read the record back through an independent path and assert round-trip
    shard_id = out["ShardId"]
    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream_name,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })["ShardIterator"]

    found = None
    for _ in range(10):
        recs = kinesis.rpc("GetRecords", {"ShardIterator": it, "Limit": 100})
        for r in recs.get("Records", []):
            if r["PartitionKey"] == partition_key:
                found = r
                break
        if found is not None:
            break
        it = recs["NextShardIterator"]
        time.sleep(0.3)

    assert found is not None, "put record not found on read back"
    # Empty data round-trips as empty base64 string
    assert found["Data"] == ""
    assert found["PartitionKey"] == partition_key

    # cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass