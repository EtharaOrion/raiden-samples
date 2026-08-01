def test_delete_alias_nonexistent_alias_not_found(cli, kms):
    alias_name = "alias/nonexistent-alias-for-delete-test-xyz"

    # Ensure the alias does not exist beforehand
    existing = kms.rpc("ListAliases", {})
    names = [a.get("AliasName") for a in existing.get("Aliases", [])]
    assert alias_name not in names

    result = cli("kms", "delete-alias", "--alias-name", alias_name)

    assert result.returncode != 0
    assert "NotFound" in result.stderr

    # Verify no alias was created/left behind
    after = kms.rpc("ListAliases", {})
    after_names = [a.get("AliasName") for a in after.get("Aliases", [])]
    assert alias_name not in after_names