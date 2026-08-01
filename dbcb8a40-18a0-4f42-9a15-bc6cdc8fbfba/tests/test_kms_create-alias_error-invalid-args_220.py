def test_create_alias_missing_target_key_id(cli, kms):
    alias_name = "alias/MissingTargetTest"

    result = cli("kms", "create-alias", "--alias-name", alias_name)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "target-key-id" in result.stderr.lower() or "argument" in result.stderr.lower()

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("AliasName") != alias_name for a in aliases)