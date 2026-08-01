def test_remove_tags_from_stream_error_nonexistent(cli, kinesis):
    stream_name = "nonexistent-stream-remove-tags-xyz"

    # Ensure the stream does not exist
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Confirm it's absent
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        stream_exists = True
    except Exception:
        stream_exists = False
    assert not stream_exists, "prerequisite: stream must not exist"

    result = cli(
        "kinesis",
        "remove-tags-from-stream",
        "--stream-name",
        stream_name,
        "--tag-keys",
        "foo",
        "bar",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert the stream is still absent
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        still_exists = True
    except Exception:
        still_exists = False
    assert not still_exists