def test_get_shard_iterator_invalid_shard_id(cli, kinesis):
    stream_name = "test-gsi-invalid-shard"
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass
    kinesis.rpc("CreateStream", {"StreamName": stream_name, "ShardCount": 1})

    result = cli(
        "kinesis", "get-shard-iterator",
        "--stream-name", stream_name,
        "--shard-id", "",
        "--shard-iterator-type", "TRIM_HORIZON",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert (
        "exception" in stderr
        or "notfound" in stderr
        or "invalid" in stderr
    )

    desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    assert desc["StreamDescription"]["StreamName"] == stream_name

    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass