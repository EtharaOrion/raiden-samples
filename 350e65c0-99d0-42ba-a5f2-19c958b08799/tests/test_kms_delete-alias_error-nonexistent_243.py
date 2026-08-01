def test_delete_alias_error_nonexistent(cli, kms, tmp_path):
    alias_name = "alias/nonexistent-alias-xyz-98765"

    # Ensure the alias does not exist beforehand
    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert alias_name not in [a.get("AliasName") for a in aliases]

    result = cli("kms", "delete-alias", "--alias-name", alias_name)

    assert result.returncode != 0
    assert "NotFoundException" in result.stderr

    # Confirm the alias still does not exist
    aliases_after = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert alias_name not in [a.get("AliasName") for a in aliases_after]