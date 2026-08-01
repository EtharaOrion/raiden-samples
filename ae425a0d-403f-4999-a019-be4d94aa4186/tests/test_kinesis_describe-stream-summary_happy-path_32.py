def test_describe_stream_summary_happy_path(cli, kinesis, tmp_path):
    import json

    stream_name = "test-dss-happy-stream"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli("kinesis", "describe-stream-summary", "--stream-name", stream_name)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    summary = out["StreamDescriptionSummary"]
    assert summary["StreamName"] == stream_name
    assert summary["StreamStatus"] in ("CREATING", "ACTIVE")

    state = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    sds = state["StreamDescriptionSummary"]
    assert sds["StreamName"] == stream_name
    assert sds["StreamStatus"] in ("CREATING", "ACTIVE")