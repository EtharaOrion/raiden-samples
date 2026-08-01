def test_enable_key_nonexistent_returns_not_found(cli, kms):
    fake_key_id = "00000000-1111-2222-3333-444455556666"
    result = cli("kms", "enable-key", "--key-id", fake_key_id)
    assert result.returncode != 0
    assert "NotFound" in result.stderr