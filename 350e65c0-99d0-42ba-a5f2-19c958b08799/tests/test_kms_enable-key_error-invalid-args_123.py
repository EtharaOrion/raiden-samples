def test_enable_key_nonexistent_key_not_found(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Ensure the key really does not exist
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("precondition failed: key unexpectedly exists")
    except Exception:
        pass

    result = cli("kms", "enable-key", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert "NotFoundException" in result.stderr