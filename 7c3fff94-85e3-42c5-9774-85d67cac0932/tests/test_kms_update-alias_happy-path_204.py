def test_update_alias_reassociates_alias_with_new_key(cli, kms):
    original_key = kms.rpc("CreateKey", {
        "Description": "Original key for update-alias test"
    })["KeyMetadata"]
    replacement_key = kms.rpc("CreateKey", {
        "Description": "Replacement key for update-alias test"
    })["KeyMetadata"]

    alias_name = "alias/update-alias-" + original_key["KeyId"]
    kms.rpc("CreateAlias", {
        "AliasName": alias_name,
        "TargetKeyId": original_key["KeyId"],
    })

    before = kms.rpc("DescribeKey", {"KeyId": alias_name})["KeyMetadata"]
    assert before["KeyId"] == original_key["KeyId"]

    result = cli(
        "kms",
        "update-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        replacement_key["KeyId"],
    )
    assert result.returncode == 0

    after = kms.rpc("DescribeKey", {"KeyId": alias_name})["KeyMetadata"]
    assert after["KeyId"] == replacement_key["KeyId"]

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    updated_alias = next(
        alias_entry
        for alias_entry in aliases
        if alias_entry["AliasName"] == alias_name
    )
    assert updated_alias["TargetKeyId"] == replacement_key["KeyId"]