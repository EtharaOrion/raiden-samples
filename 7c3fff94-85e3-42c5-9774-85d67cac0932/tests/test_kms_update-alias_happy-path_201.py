def test_update_alias_reassociates_existing_alias(cli, kms):
    original_key = kms.rpc("CreateKey", {})["KeyMetadata"]
    replacement_key = kms.rpc("CreateKey", {})["KeyMetadata"]
    assert original_key["KeyId"] != replacement_key["KeyId"]

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