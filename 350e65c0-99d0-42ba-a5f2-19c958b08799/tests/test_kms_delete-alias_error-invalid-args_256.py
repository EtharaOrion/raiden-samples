def test_delete_alias_invalid_alias_name_too_long(cli, kms):
    long_name = "x" * 300
    alias_name = "alias/" + long_name
    result = cli("kms", "delete-alias", "--alias-name", alias_name)
    assert result.returncode != 0
    assert "Exception" in result.stderr or "ValidationException" in result.stderr