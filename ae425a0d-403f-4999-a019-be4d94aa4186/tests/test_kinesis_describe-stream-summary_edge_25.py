def test_describe_stream_summary_returns_summary(cli, kinesis):
    import json
    stream_name = "test-summary-stream-x"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli("kinesis", "describe-stream-summary", "--stream-name", stream_name)
    assert result.returncode == 0

    out = json.loads(result.stdout)
    summary = out["StreamDescriptionSummary"]
    assert summary["StreamName"] == stream_name
    assert summary["StreamStatus"] in ("CREATING", "ACTIVE")

    described = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    desc_summary = described["StreamDescriptionSummary"]
    assert desc_summary["StreamName"] == stream_name
    assert desc_summary["StreamStatus"] in ("CREATING", "ACTIVE")

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass