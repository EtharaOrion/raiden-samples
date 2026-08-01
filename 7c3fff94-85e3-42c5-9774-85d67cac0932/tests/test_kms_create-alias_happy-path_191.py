def test_create_alias_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "key for create-alias test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/pytest-create-alias-{key_id}"

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert not any(alias.get("AliasName") == alias_name for alias in aliases_before)

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        key_id,
    )
    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    created_alias = next(
        alias for alias in aliases_after if alias.get("AliasName") == alias_name
    )
    assert created_alias["TargetKeyId"] == key_id