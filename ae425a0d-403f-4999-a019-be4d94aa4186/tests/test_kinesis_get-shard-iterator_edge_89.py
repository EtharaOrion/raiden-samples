def test_get_shard_iterator_after_sequence_number(cli, kinesis, tmp_path):
    import base64
    import json
    import time

    stream = "test-gsi-after-seq-stream"
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
        if sd["StreamStatus"] == "ACTIVE" and sd.get("Shards"):
            shard_id = sd["Shards"][0]["ShardId"]
            break
        time.sleep(0.2)
    assert shard_id is not None, "stream never became ACTIVE with shards"

    # Put a record so we have a sequence number
    data = base64.b64encode(b"hello-world").decode("ascii")
    put = kinesis.rpc(
        "PutRecord",
        {"StreamName": stream, "Data": data, "PartitionKey": "pk-1"},
    )
    seq = put["SequenceNumber"]

    result = cli(
        "kinesis",
        "get-shard-iterator",
        "--stream-name",
        stream,
        "--shard-id",
        shard_id,
        "--shard-iterator-type",
        "AFTER_SEQUENCE_NUMBER",
        "--starting-sequence-number",
        seq,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    iterator = out["ShardIterator"]
    assert isinstance(iterator, str) and iterator

    # Independently verify the iterator is usable via the raw client.
    got = kinesis.rpc("GetRecords", {"ShardIterator": iterator})
    assert "Records" in got
    assert "NextShardIterator" in got

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass