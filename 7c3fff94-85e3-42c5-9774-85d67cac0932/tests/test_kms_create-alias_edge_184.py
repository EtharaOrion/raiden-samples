def test_create_alias_with_valid_name(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "create-alias edge test"})
    key_id = created["KeyMetadata"]["KeyId"]
    alias_name = f"alias/x-{key_id}"

    before = kms.rpc("ListAliases", {})
    assert not any(
        alias.get("AliasName") == alias_name
        for alias in before["Aliases"]
    )

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        key_id,
    )
    assert result.returncode == 0

    after = kms.rpc("ListAliases", {})
    matching = [
        alias
        for alias in after["Aliases"]
        if alias.get("AliasName") == alias_name
    ]
    assert len(matching) == 1
    assert matching[0]["TargetKeyId"] == key_id