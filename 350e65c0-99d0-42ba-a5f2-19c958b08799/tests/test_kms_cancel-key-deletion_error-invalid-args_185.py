def test_cancel_key_deletion_invalid_key_id(cli, kms):
    bad_key_id = "x" * 300
    result = cli("kms", "cancel-key-deletion", "--key-id", bad_key_id)
    assert result.returncode != 0
    assert "Exception" in result.stderr or "InvalidArn" in result.stderr or "NotFound" in result.stderr