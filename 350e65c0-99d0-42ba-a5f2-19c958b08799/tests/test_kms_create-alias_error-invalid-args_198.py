def test_create_alias_missing_target_key_id(cli, kms):
    alias_name = "alias/test-missing-target-key"

    result = cli("kms", "create-alias", "--alias-name", alias_name)

    assert result.returncode != 0
    assert "target-key-id" in result.stderr.lower() or "targetkeyid" in result.stderr.lower()

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("AliasName") != alias_name for a in aliases)