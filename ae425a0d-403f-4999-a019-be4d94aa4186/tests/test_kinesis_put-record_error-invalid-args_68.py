def test_put_record_invalid_flag_rejected(cli, kinesis, tmp_path):
    stream = "test-put-record-invalid-flag"
    kinesis.rpc("CreateStream", {"StreamName": stream, "ShardCount": 1})

    result = cli(
        "kinesis", "put-record",
        "--stream-name", stream,
        "--data", "aGVsbG8=",
        "--partition-key", "pk1",
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "not-a-real-flag" in result.stderr or "Unknown" in result.stderr or "unrecognized" in result.stderr.lower()

    kinesis.rpc("DeleteStream", {"StreamName": stream})