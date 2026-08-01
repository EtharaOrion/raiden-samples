import json
import base64
import time
import uuid


def test_put_records_happy_path(cli, kinesis):
    stream_name = "test-put-records-" + uuid.uuid4().hex[:8]
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    # Wait for ACTIVE so we can read records back
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
        raise AssertionError("stream never became ACTIVE")

    try:
        data1 = base64.b64encode(b"hello-world").decode()
        data2 = base64.b64encode(b"second-record").decode()
        records = [
            {"Data": data1, "PartitionKey": "pk1"},
            {"Data": data2, "PartitionKey": "pk2"},
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

        # Read the records back independently and assert round-trip
        shards = kinesis.rpc("DescribeStream", {"StreamName": stream_name})["StreamDescription"]["Shards"]
        assert shards, "no shards on ACTIVE stream"

        found = {}
        for shard in shards:
            shard_id = shard["ShardId"]
            it = kinesis.rpc("GetShardIterator", {
                "StreamName": stream_name,
                "ShardId": shard_id,
                "ShardIteratorType": "TRIM_HORIZON",
            })["ShardIterator"]

            for _ in range(5):
                resp = kinesis.rpc("GetRecords", {"ShardIterator": it, "Limit": 100})
                for rec in resp.get("Records", []):
                    found[rec["PartitionKey"]] = rec["Data"]
                it = resp["NextShardIterator"]
                if not resp.get("Records"):
                    break

        assert found.get("pk1") == data1
        assert found.get("pk2") == data2
    finally:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})