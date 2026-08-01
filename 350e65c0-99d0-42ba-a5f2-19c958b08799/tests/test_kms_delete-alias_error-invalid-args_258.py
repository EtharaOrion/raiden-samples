def test_delete_alias_missing_alias_not_found(cli, kms):
    alias_name = "alias/nonexistent-test-alias-xyz"
    existing = kms.rpc("ListAliases", {})
    assert alias_name not in [a["AliasName"] for a in existing.get("Aliases", [])]

    result = cli("kms", "delete-alias", "--alias-name", alias_name)

    assert result.returncode != 0
    assert "NotFound" in result.stderr

    after = kms.rpc("ListAliases", {})
    assert alias_name not in [a["AliasName"] for a in after.get("Aliases", [])]