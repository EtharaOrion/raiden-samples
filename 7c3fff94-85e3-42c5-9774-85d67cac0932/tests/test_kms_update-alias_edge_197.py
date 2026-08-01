def test_update_alias_retargets_existing_alias(cli, kms):
    original_key = kms.rpc("CreateKey", {
        "Description": "original alias target",
    })["KeyMetadata"]
    replacement_key = kms.rpc("CreateKey", {
        "Description": "replacement alias target",
    })["KeyMetadata"]
    alias_name = "alias/update-alias-edge"

    kms.rpc("CreateAlias", {
        "AliasName": alias_name,
        "TargetKeyId": original_key["KeyId"],
    })

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    alias_before = next(
        alias_entry
        for alias_entry in aliases_before
        if alias_entry["AliasName"] == alias_name
    )
    assert alias_before["TargetKeyId"] == original_key["KeyId"]
    assert original_key["KeyId"] != replacement_key["KeyId"]

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
    matching_aliases = [
        alias_entry
        for alias_entry in aliases_after
        if alias_entry["AliasName"] == alias_name
    ]
    assert len(matching_aliases) == 1
    assert matching_aliases[0]["TargetKeyId"] == replacement_key["KeyId"]

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})["KeyMetadata"]
    assert described["KeyId"] == replacement_key["KeyId"]