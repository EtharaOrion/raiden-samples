def test_delete_alias_missing_required_arg(cli, kms):
    result = cli("kms", "delete-alias")
    assert result.returncode != 0
    assert "alias-name" in result.stderr.lower() or "required" in result.stderr.lower()