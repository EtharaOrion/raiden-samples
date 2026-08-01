def test_create_alias_target_key_not_found(cli, kms, tmp_path):
    # Use a non-existent target key id so CreateAlias fails.
    fake_key_id = "00000000-1111-2222-3333-444444444444"
    alias_name = "alias/test-missing-target-%s" % fake_key_id[:8]

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", fake_key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    # Assert the alias was NOT created in the resulting state.
    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("AliasName") != alias_name for a in aliases)