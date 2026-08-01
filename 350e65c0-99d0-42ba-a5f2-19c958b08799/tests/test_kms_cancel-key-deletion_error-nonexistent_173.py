def test_cancel_key_deletion_error_nonexistent(cli, kms):
    missing_key_id = "12345678-1234-1234-1234-123456789012"

    # Ensure the key really does not exist
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        raise AssertionError("precondition failed: key unexpectedly exists")
    except Exception:
        pass

    result = cli("kms", "cancel-key-deletion", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert "NotFoundException" in result.stderr