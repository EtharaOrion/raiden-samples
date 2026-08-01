def test_create_alias_nonexistent_target_key(cli, kms):
    alias_name = "alias/test-nonexistent-target-alias"
    fake_key_id = "00000000-1111-2222-3333-444444444444"

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", fake_key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert not any(a.get("AliasName") == alias_name for a in aliases)