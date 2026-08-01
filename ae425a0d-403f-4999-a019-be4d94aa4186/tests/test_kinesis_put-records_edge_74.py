import base64
import json
import time


def test_put_records_roundtrip(cli, kinesis, tmp_path):
    stream_name = "test-put-records-stream"

    # Clean up any pre-existing stream
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Seed prerequisite state: create the stream
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Poll until ACTIVE (read path requires active stream)
    deadline = time.time() + 30
    status = None
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        status = desc["StreamDescription"]["StreamStatus"]
        if status == "ACTIVE":
            break
        time.sleep(0.5)
    assert status == "ACTIVE"

    # Prepare record data
    data_plain = b"hello-put-records"
    data_b64 = base64.b64encode(data_plain).decode("ascii")
    partition_key = "pk-1"

    records_arg = json.dumps(
        [{"Data": data_b64, "PartitionKey": partition_key}]
    )

    # Run the command under test
    result = cli(
        "kinesis",
        "put-records",
        "--stream-name",
        stream_name,
        "--records",
        records_arg,
    )
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert out["FailedRecordCount"] == 0
    assert len(out["Records"]) == 1

    # Read the record back via an independent path (GetShardIterator + GetRecords)
    shards = kinesis.rpc("ListShards", {"StreamName": stream_name})["Shards"]
    assert len(shards) >= 1
    shard_id = shards[0]["ShardId"]

    it = kinesis.rpc(
        "GetShardIterator",
        {
            "StreamName": stream_name,
            "ShardId": shard_id,
            "ShardIteratorType": "TRIM_HORIZON",
        },
    )["ShardIterator"]

    found = False
    deadline = time.time() + 20
    while time.time() < deadline and not found:
        resp = kinesis.rpc("GetRecords", {"ShardIterator": it, "Limit": 100})
        for rec in resp.get("Records", []):
            if rec["Data"] == data_b64 and rec["PartitionKey"] == partition_key:
                found = True
                break
        it = resp.get("NextShardIterator")
        if it is None:
            break
        if not found:
            time.sleep(0.5)

    assert found, "put record not found via GetRecords round trip"

    # Clean up
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass