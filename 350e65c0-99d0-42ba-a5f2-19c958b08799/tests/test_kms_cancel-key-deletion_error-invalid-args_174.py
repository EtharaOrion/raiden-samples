def test_cancel_key_deletion_missing_required_key_id(cli, kms):
    result = cli("kms", "cancel-key-deletion")
    assert result.returncode != 0
    assert "key-id" in result.stderr.lower()