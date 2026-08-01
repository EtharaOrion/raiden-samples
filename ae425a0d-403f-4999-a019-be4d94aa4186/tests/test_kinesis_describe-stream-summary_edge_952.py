def test_describe_stream_summary_reports_shard_count(cli, kinesis):
    import json
    import re
    import uuid
    import time

    name = "summary-shape-" + uuid.uuid4().hex[:8]
    kinesis.rpc("CreateStream", {"StreamName": name, "ShardCount": 3})

    # wait for asynchronous stream creation to settle before asserting on it
    for _ in range(100):
        _sd = kinesis.rpc("DescribeStream", {"StreamName": name})["StreamDescription"]
        if _sd["StreamStatus"] == "ACTIVE" and len(_sd.get("Shards", [])) == 3:
            break
        time.sleep(0.2)
    else:
        raise AssertionError("stream %s never became ACTIVE" % name)

    result = cli("kinesis", "describe-stream-summary", "--stream-name", name)
    assert result.returncode == 0, result.stderr

    s = json.loads(result.stdout)["StreamDescriptionSummary"]

    assert s["StreamName"] == name
    assert s["StreamStatus"] == "ACTIVE"
    assert s["OpenShardCount"] == 3
    assert s["RetentionPeriodHours"] == 24
    assert s["ConsumerCount"] == 0
    assert s["EncryptionType"]
    assert re.fullmatch(
        r"arn:aws:kinesis:[a-z0-9-]+:\d{12}:stream/" + re.escape(name), s["StreamARN"]
    )

    kinesis.rpc("DeleteStream", {"StreamName": name})
