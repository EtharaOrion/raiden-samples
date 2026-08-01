def test_describe_key_missing_required_key_id(cli, kms):
    result = cli("kms", "describe-key")
    assert result.returncode != 0
    assert "key-id" in result.stderr.lower() or "required" in result.stderr.lower()