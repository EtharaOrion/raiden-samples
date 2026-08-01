def test_create_alias_invalid_target_key_not_found(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"
    alias_name = "alias/nonexistent-target-test"

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", missing_key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("AliasName") != alias_name for a in aliases)