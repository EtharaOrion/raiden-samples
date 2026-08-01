def test_get_shard_iterator_at_sequence_number(cli, kinesis, tmp_path):
    import json
    import time
    import base64

    stream = "test-getsharditer-atseq"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
    time.sleep(0.2)

    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    # Poll until ACTIVE so shards are populated
    shard_id = None
    for _ in range(50):
        try:
            desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
        except Exception:
            time.sleep(0.2)
            continue
        sd = desc["StreamDescription"]
        if sd["StreamStatus"] == "ACTIVE" and sd["Shards"]:
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.2)
    assert shard_id is not None

    # Put a record to obtain a real sequence number
    data = base64.b64encode(b"hello-world").decode()
    put = kinesis.rpc("PutRecord", {
        "StreamName": stream,
        "Data": data,
        "PartitionKey": "pk1",
    })
    seq = put["SequenceNumber"]

    result = cli(
        "kinesis", "get-shard-iterator",
        "--stream-name", stream,
        "--shard-id", shard_id,
        "--shard-iterator-type", "AT_SEQUENCE_NUMBER",
        "--starting-sequence-number", seq,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "ShardIterator" in out
    iterator = out["ShardIterator"]
    assert isinstance(iterator, str) and iterator

    # Independently verify the iterator reads back the record we put
    got = kinesis.rpc("GetRecords", {"ShardIterator": iterator})
    records = got["Records"]
    assert any(r["Data"] == data and r["PartitionKey"] == "pk1" for r in records)

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass