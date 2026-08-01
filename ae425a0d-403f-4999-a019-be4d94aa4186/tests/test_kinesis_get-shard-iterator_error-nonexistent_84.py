def test_get_shard_iterator_nonexistent(cli, kinesis):
    stream_name = "nonexistent-stream-xyz-12345"
    # Ensure the stream does not exist
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass
    # Confirm absence via DescribeStream
    missing = False
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
    except Exception:
        missing = True
    assert missing

    result = cli(
        "kinesis", "get-shard-iterator",
        "--stream-name", stream_name,
        "--shard-id", "shardId-000000000000",
        "--shard-iterator-type", "TRIM_HORIZON",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr