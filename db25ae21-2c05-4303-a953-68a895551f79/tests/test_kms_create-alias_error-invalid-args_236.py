def test_create_alias_already_exists(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    alias_name = "alias/dup-alias-" + key_id[:8]
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    # Verify seeded alias exists
    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(a["AliasName"] == alias_name for a in aliases)

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "AlreadyExistsException" in result.stderr

    # State unchanged: alias still points to original key
    aliases_after = [
        a for a in kms.rpc("ListAliases", {})["Aliases"]
        if a["AliasName"] == alias_name
    ]
    assert len(aliases_after) == 1
    assert aliases_after[0].get("TargetKeyId") == key_id