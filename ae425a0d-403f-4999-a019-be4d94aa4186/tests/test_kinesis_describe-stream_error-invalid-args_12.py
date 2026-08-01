def test_describe_stream_empty_stream_name_error(cli, kinesis):
    result = cli("kinesis", "describe-stream", "--stream-name", "")
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr.lower()
    assert (
        "exception" in stderr
        or "notfound" in stderr
        or "invalid" in stderr
        or "validation" in stderr
    )