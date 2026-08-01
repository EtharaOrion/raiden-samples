import json
import base64
import time


def test_put_records_happy_path(cli, kinesis, tmp_path):
    stream = "test-put-records-stream"
    # cleanup any pre-existing state
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
    time.sleep(0.2)

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # wait until ACTIVE so we can read records back
    for _ in range(30):
        try:
            desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
        except Exception:
            time.sleep(0.2)
            continue
        status = desc["StreamDescription"]["StreamStatus"]
        if status == "ACTIVE":
            break
        time.sleep(0.3)

    data1 = base64.b64encode(b"hello-world-one").decode("ascii")
    data2 = base64.b64encode(b"hello-world-two").decode("ascii")
    pk1 = "partition-1"
    pk2 = "partition-2"

    records = [
        {"Data": data1, "PartitionKey": pk1},
        {"Data": data2, "PartitionKey": pk2},
    ]

    result = cli(
        "kinesis", "put-records",
        "--stream-name", stream,
        "--records", json.dumps(records),
    )

    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert out["FailedRecordCount"] == 0
    assert len(out["Records"]) == len(records)

    # Independently read the records back from the stream and verify round trip.
    desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
    shards = desc["StreamDescription"]["Shards"]
    assert shards, "expected ACTIVE stream to expose shards"
    shard_id = shards[0]["ShardId"]

    it = kinesis.rpc("GetShardIterator", {
        "StreamName": stream,
        "ShardId": shard_id,
        "ShardIteratorType": "TRIM_HORIZON",
    })
    shard_iterator = it["ShardIterator"]

    seen = {}
    for _ in range(10):
        recs = kinesis.rpc("GetRecords", {"ShardIterator": shard_iterator, "Limit": 100})
        for r in recs.get("Records", []):
            seen[r["PartitionKey"]] = r["Data"]
        if pk1 in seen and pk2 in seen:
            break
        shard_iterator = recs["NextShardIterator"]
        time.sleep(0.3)

    assert pk1 in seen
    assert pk2 in seen
    assert seen[pk1] == data1
    assert seen[pk2] == data2

    # cleanup
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass