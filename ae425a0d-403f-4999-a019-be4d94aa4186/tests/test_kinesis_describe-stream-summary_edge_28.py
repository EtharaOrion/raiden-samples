def test_describe_stream_summary_long_stream_name(cli, kinesis):
    stream_name = "x" * 128
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli("kinesis", "describe-stream-summary", "--stream-name", stream_name)

    assert result.returncode == 0

    import json
    parsed = json.loads(result.stdout)
    summary = parsed["StreamDescriptionSummary"]
    assert summary["StreamName"] == stream_name
    assert summary["StreamStatus"] in ("CREATING", "ACTIVE")

    described = kinesis.rpc("DescribeStreamSummary", {"StreamName": stream_name})
    desc_summary = described["StreamDescriptionSummary"]
    assert desc_summary["StreamName"] == stream_name
    assert desc_summary["StreamStatus"] in ("CREATING", "ACTIVE")

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})