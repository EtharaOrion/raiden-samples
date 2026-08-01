def test_enable_key_missing_required_key_id(cli, kms):
    result = cli("kms", "enable-key")
    assert result.returncode != 0
    assert "key-id" in result.stderr.lower() or "keyid" in result.stderr.lower()