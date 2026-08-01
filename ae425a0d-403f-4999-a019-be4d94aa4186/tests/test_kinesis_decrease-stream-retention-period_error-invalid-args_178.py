def test_decrease_stream_retention_period_invalid_args(cli, kinesis, tmp_path):
    result = cli(
        "kinesis", "decrease-stream-retention-period",
        "--retention-period-hours", "48",
        "--attribute-definitions", "{not valid json",
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr or "attribute-definitions" in result.stderr