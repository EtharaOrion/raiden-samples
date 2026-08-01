def test_create_alias_already_exists(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    alias_name = "alias/dup-alias-test-key"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    # sanity: alias exists and points at our key
    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert match, "prerequisite alias was not created"
    assert match[0].get("TargetKeyId") == key_id

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "AlreadyExistsException" in result.stderr

    # state unchanged: alias still points at the original key, no duplicates
    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    matches_after = [a for a in aliases_after if a["AliasName"] == alias_name]
    assert len(matches_after) == 1
    assert matches_after[0].get("TargetKeyId") == key_id