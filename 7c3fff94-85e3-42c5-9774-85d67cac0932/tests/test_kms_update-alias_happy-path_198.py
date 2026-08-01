def test_update_alias_reassociates_alias_with_new_key(cli, kms):
    original_key = kms.rpc(
        "CreateKey",
        {"Description": "Original key for update-alias test"},
    )["KeyMetadata"]
    replacement_key = kms.rpc(
        "CreateKey",
        {"Description": "Replacement key for update-alias test"},
    )["KeyMetadata"]

    alias_name = f"alias/update-alias-{original_key['KeyId']}"
    kms.rpc(
        "CreateAlias",
        {
            "AliasName": alias_name,
            "TargetKeyId": original_key["KeyId"],
        },
    )

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    matching_before = [
        alias for alias in aliases_before if alias["AliasName"] == alias_name
    ]
    assert len(matching_before) == 1
    assert matching_before[0]["TargetKeyId"] == original_key["KeyId"]

    result = cli(
        "kms",
        "update-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        replacement_key["KeyId"],
    )

    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    matching_after = [
        alias for alias in aliases_after if alias["AliasName"] == alias_name
    ]
    assert len(matching_after) == 1
    assert matching_after[0]["TargetKeyId"] == replacement_key["KeyId"]