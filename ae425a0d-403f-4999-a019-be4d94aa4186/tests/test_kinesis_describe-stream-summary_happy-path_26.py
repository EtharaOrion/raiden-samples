def test_describe_stream_summary_happy_path(cli, kinesis, tmp_path):
    stream_name = "test-summary-stream-happy"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli("kinesis", "describe-stream-summary", "--stream-name", stream_name)
    assert result.returncode == 0

    import json
    out = json.loads(result.stdout)
    summary = out["StreamDescriptionSummary"]
    assert summary["StreamName"] == stream_name
    assert summary["StreamStatus"] in ("CREATING", "ACTIVE")

    # Independent read-back via raw client
    desc = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    sds = desc["StreamDescriptionSummary"]
    assert sds["StreamName"] == stream_name
    assert sds["StreamStatus"] in ("CREATING", "ACTIVE")

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})