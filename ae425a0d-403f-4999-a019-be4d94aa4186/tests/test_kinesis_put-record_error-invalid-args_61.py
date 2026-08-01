def test_put_record_missing_required_data_arg(cli, kinesis, tmp_path):
    stream_name = "test-stream-missing-data-arg"
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli(
        "kinesis", "put-record",
        "--stream-name", stream_name,
        "--partition-key", "pk-1",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "data" in result.stderr.lower()

    # Stream state should be unaffected by the failed call
    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    assert desc["StreamDescription"]["StreamName"] == stream_name

    kinesis.rpc("DeleteStream", {"StreamName": stream_name})