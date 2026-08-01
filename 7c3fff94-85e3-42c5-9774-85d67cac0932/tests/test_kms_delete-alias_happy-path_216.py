def test_delete_alias_removes_alias_without_deleting_key(cli, kms):
    key_metadata = kms.rpc(
        "CreateKey",
        {"Description": "Key for delete-alias happy-path test"},
    )["KeyMetadata"]
    key_id = key_metadata["KeyId"]
    alias_name = f"alias/delete-alias-{key_id}"

    kms.rpc(
        "CreateAlias",
        {"AliasName": alias_name, "TargetKeyId": key_id},
    )
    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias.get("AliasName") == alias_name
        and alias.get("TargetKeyId") == key_id
        for alias in aliases_before
    )

    result = cli(
        "kms",
        "delete-alias",
        "--alias-name",
        alias_name,
    )

    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert all(alias.get("AliasName") != alias_name for alias in aliases_after)

    remaining_key = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert remaining_key["KeyId"] == key_id