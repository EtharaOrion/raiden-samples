def test_put_record_acknowledges_shard_and_sequence(cli, kinesis):
    import json
    import re
    import uuid
    import time

    name = "put-ack-" + uuid.uuid4().hex[:8]
    kinesis.rpc("CreateStream", {"StreamName": name, "ShardCount": 1})

    # wait for asynchronous stream creation to settle before asserting on it
    for _ in range(100):
        _sd = kinesis.rpc("DescribeStream", {"StreamName": name})["StreamDescription"]
        if _sd["StreamStatus"] == "ACTIVE" and len(_sd.get("Shards", [])) == 1:
            break
        time.sleep(0.2)
    else:
        raise AssertionError("stream %s never became ACTIVE" % name)

    result = cli("kinesis", "put-record", "--stream-name", name,
                 "--data", "aGVsbG8=", "--partition-key", "pk-1")
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert set(out) == {"ShardId", "SequenceNumber"}
    assert re.fullmatch(r"shardId-\d{12}", out["ShardId"])
    assert out["SequenceNumber"].isdigit()
    assert len(out["SequenceNumber"]) > 20

    kinesis.rpc("DeleteStream", {"StreamName": name})
