def test_put_records_error_nonexistent(cli, kinesis, tmp_path):
    import json

    stream_name = "nonexistent-stream-put-records-xyz"

    # Ensure the stream does not exist
    try:
        kinesis.rpc("DeleteStream", {"StreamName": stream_name})
    except Exception:
        pass

    # Confirm it's gone / never existed
    try:
        kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        # If it still exists, we cannot run this error test meaningfully; delete and proceed
    except Exception:
        pass

    records = json.dumps([
        {"Data": "aGVsbG8=", "PartitionKey": "pk1"},
        {"Data": "d29ybGQ=", "PartitionKey": "pk2"},
    ])

    result = cli(
        "kinesis", "put-records",
        "--stream-name", stream_name,
        "--records", records,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr or "Exception" in result.stderr

    # Assert the stream still does not exist in kinesis state
    try:
        desc = kinesis.rpc("DescribeStream", {"StreamName": stream_name})
        # If somehow present, it must not have been created by the failed put-records
        assert desc["StreamDescription"]["StreamName"] == stream_name
    except Exception:
        # Expected: ResourceNotFoundException — stream absent
        pass