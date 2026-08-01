def test_create_alias_target_not_found(cli, kms):
    # Use a well-formed alias name but a non-existent target key id
    alias_name = "alias/orphan-alias-xyz"
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", missing_key_id,
    )

    assert result.returncode != 0
    assert "NotFound" in result.stderr

    # Assert no alias was created as a side effect
    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("AliasName") != alias_name for a in aliases)