def test_enable_key_error_nonexistent(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Ensure the key does not exist
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("precondition failed: key unexpectedly exists")
    except Exception:
        pass

    result = cli("kms", "enable-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    # Confirm no such key exists as resulting state
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("key should still not exist")
    except Exception:
        pass