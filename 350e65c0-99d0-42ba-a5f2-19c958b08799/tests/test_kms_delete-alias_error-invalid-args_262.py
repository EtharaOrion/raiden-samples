def test_delete_alias_nonexistent_not_found(cli, kms):
    alias_name = "alias/does-not-exist-xyz-12345"

    # Ensure the alias truly does not exist beforehand.
    existing = kms.rpc("ListAliases", {})
    names = {a["AliasName"] for a in existing.get("Aliases", [])}
    assert alias_name not in names

    result = cli("kms", "delete-alias", "--alias-name", alias_name)

    assert result.returncode != 0
    assert "NotFound" in result.stderr

    # State assertion: alias still absent.
    after = kms.rpc("ListAliases", {})
    after_names = {a["AliasName"] for a in after.get("Aliases", [])}
    assert alias_name not in after_names