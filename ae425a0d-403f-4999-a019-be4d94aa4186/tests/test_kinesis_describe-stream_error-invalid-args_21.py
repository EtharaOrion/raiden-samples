def test_describe_stream_limit_out_of_range(cli, kinesis):
    stream_name = "test-describe-limit-oob"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})
    try:
        result = cli(
            "kinesis", "describe-stream",
            "--stream-name", stream_name,
            "--limit", "10001",
        )
        assert result.returncode != 0
        assert not result.stdout.strip(), result.stdout
        assert "Exception" in result.stderr or "ValidationError" in result.stderr or "InvalidArgument" in result.stderr

        desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        assert desc["StreamDescription"]["StreamName"] == stream_name
    finally:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})