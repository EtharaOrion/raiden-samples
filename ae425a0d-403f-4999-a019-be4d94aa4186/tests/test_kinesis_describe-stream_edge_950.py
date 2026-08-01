def test_describe_stream_returns_full_description(cli, kinesis):
    import json
    import re
    import uuid
    import time

    name = "desc-contract-" + uuid.uuid4().hex[:8]
    kinesis.rpc("CreateStream", {"StreamName": name, "ShardCount": 2})

    # wait for asynchronous stream creation to settle before asserting on it
    for _ in range(100):
        _sd = kinesis.rpc("DescribeStream", {"StreamName": name})["StreamDescription"]
        if _sd["StreamStatus"] == "ACTIVE" and len(_sd.get("Shards", [])) == 2:
            break
        time.sleep(0.2)
    else:
        raise AssertionError("stream %s never became ACTIVE" % name)

    result = cli("kinesis", "describe-stream", "--stream-name", name)
    assert result.returncode == 0, result.stderr

    d = json.loads(result.stdout)["StreamDescription"]

    assert d["StreamName"] == name
    assert d["StreamStatus"] == "ACTIVE"
    assert d["RetentionPeriodHours"] == 24
    assert d["EncryptionType"]
    assert "EnhancedMonitoring" in d
    assert "StreamCreationTimestamp" in d
    assert re.fullmatch(
        r"arn:aws:kinesis:[a-z0-9-]+:\d{12}:stream/" + re.escape(name), d["StreamARN"]
    )

    assert len(d["Shards"]) == 2
    for shard in d["Shards"]:
        assert re.fullmatch(r"shardId-\d{12}", shard["ShardId"])
        assert shard["HashKeyRange"]["StartingHashKey"].isdigit()
        assert shard["HashKeyRange"]["EndingHashKey"].isdigit()
        assert shard["SequenceNumberRange"]["StartingSequenceNumber"].isdigit()

    kinesis.rpc("DeleteStream", {"StreamName": name})
