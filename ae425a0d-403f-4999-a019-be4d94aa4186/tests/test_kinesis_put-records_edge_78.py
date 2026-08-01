import json
import base64
import time


def test_put_records_multiple_entries(cli, kinesis):
    stream_name = "test-put-records-edge-stream"

    # Clean up any pre-existing stream
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Prerequisite: create the stream and wait for ACTIVE (read path needs ACTIVE)
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    deadline = time.time() + 30
    shard_id = None
    while time.time() < deadline:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.5)
    assert shard_id is not None, "stream did not become ACTIVE"

    # Grab a TRIM_HORIZON iterator BEFORE putting records
    it_resp = kinesis.rpc(
        "GetShardIterator",
        {
            "StreamName": stream_name,
            "ShardId": shard_id,
            "ShardIteratorType": "TRIM_HORIZON",
        },
    )
    shard_iterator = it_resp["ShardIterator"]

    # Prepare records for the CLI call
    pk1 = "pk-one"
    pk2 = "pk-two"
    raw1 = b"hello-record-one"
    raw2 = b"hello-record-two"
    b64_1 = base64.b64encode(raw1).decode("ascii")
    b64_2 = base64.b64encode(raw2).decode("ascii")

    records_arg = json.dumps(
        [
            {"Data": b64_1, "PartitionKey": pk1},
            {"Data": b64_2, "PartitionKey": pk2},
        ]
    )

    # Command under test
    result = cli(
        "kinesis",
        "put-records",
        "--stream-name",
        stream_name,
        "--records",
        records_arg,
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out.get("FailedRecordCount") == 0
    assert len(out.get("Records", [])) == 2

    # Independent read-back: poll GetRecords to observe the round-trip
    seen = {}
    it = shard_iterator
    read_deadline = time.time() + 30
    while time.time() < read_deadline and len(seen) < 2:
        gr = kinesis.rpc("GetRecords", {"ShardIterator": it, "Limit": 100})
        for rec in gr.get("Records", []):
            seen[rec["PartitionKey"]] = rec["Data"]
        it = gr["NextShardIterator"]
        if len(seen) >= 2:
            break
        time.sleep(0.5)

    assert pk1 in seen
    assert pk2 in seen
    assert seen[pk1] == b64_1
    assert seen[pk2] == b64_2

    # Cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass