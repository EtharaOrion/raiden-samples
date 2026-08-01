def test_add_tags_to_stream_nonexistent(cli, kinesis):
    stream_name = "nonexistent-stream-for-tags-test-xyz"

    # Ensure the stream does not exist
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Confirm it's absent
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        stream_present = True
    except Exception:
        stream_present = False
    assert not stream_present

    result = cli(
        "kinesis", "add-tags-to-stream",
        "--stream-name", stream_name,
        "--tags", '{"env":"test"}',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Confirm no state leaked: stream still absent
    try:
        kinesis.rpc("ListTagsForStream", {"StreamName": stream_name})
        still_present = True
    except Exception:
        still_present = False
    assert not still_present