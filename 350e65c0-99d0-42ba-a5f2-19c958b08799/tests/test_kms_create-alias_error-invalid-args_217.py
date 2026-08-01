def test_create_alias_invalid_target_key_notfound(cli, kms):
    # Attempt to create an alias pointing at a nonexistent target key.
    missing_key_id = "00000000-1111-2222-3333-444444444444"
    alias_name = "alias/test-orphan-alias-xyz"

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", missing_key_id,
    )

    assert result.returncode != 0
    assert "NotFound" in result.stderr

    # Assert no such alias got created in the backend state.
    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("AliasName") != alias_name for a in aliases)