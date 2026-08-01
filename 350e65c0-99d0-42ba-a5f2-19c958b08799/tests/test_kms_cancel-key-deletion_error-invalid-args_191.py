def test_cancel_key_deletion_not_found_key(cli, kms):
    # Use a well-formed but non-existent key id to trigger a service error
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    result = cli("kms", "cancel-key-deletion", "--key-id", missing_key_id)

    assert result.returncode != 0
    assert "NotFound" in result.stderr

    # Confirm the key genuinely does not exist in kms state
    try:
        kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        described = True
    except Exception:
        described = False
    assert described is False