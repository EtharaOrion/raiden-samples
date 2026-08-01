def test_create_alias_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    alias_name = "alias/happy-path-test-alias"
    result = cli("kms", "create-alias", "--alias-name", alias_name, "--target-key-id", key_id)
    assert result.returncode == 0

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert match, f"alias {alias_name} not found in {aliases}"
    assert match[0].get("TargetKeyId") == key_id