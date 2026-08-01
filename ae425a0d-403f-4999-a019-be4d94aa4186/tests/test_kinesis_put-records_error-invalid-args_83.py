def test_put_records_invalid_args(cli, kinesis):
    result = cli(
        "kinesis", "put-records",
        "--records", '[{"Data":"aGVsbG8=","PartitionKey":"pk"}]',
        "--attribute-definitions", "{not valid json",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "attribute-definitions" in result.stderr