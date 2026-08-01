def test_get_shard_iterator_invalid_flag_rejected(cli, kinesis, tmp_path):
    stream = "test-gsi-invalid-flag"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream})
    except Exception:
        pass
    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    result = cli(
        "kinesis", "get-shard-iterator",
        "--stream-name", stream,
        "--shard-id", "shardId-000000000000",
        "--shard-iterator-type", "TRIM_HORIZON",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    desc = kinesis.rpc("DescribeStream", {"StreamName": stream})
    assert desc["StreamDescription"]["StreamName"] == stream

    kinesis.rpc("DeleteStream", {"StreamName": stream})