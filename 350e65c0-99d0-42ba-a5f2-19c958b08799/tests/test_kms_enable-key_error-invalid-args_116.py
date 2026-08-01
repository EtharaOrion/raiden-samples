def test_enable_key_invalid_key_id_length(cli, kms):
    oversized_key_id = "x" * 2048
    result = cli("kms", "enable-key", "--key-id", oversized_key_id)
    assert result.returncode != 0
    assert "Exception" in result.stderr or "Invalid" in result.stderr or "NotFound" in result.stderr