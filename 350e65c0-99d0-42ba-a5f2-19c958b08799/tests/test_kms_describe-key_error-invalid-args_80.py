def test_describe_key_nonexistent_returns_not_found(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Ensure the key truly does not exist in backend state.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("precondition failed: key unexpectedly exists")
    except Exception:
        pass

    result = cli("kms", "describe-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert "NotFound" in result.stderr

    # Confirm it still does not exist as backend state.
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("key should not exist after failed describe")
    except Exception:
        pass