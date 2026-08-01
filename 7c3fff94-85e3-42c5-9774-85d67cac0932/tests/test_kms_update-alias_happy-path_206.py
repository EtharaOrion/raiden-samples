def test_update_alias_reassociates_with_new_key(cli, kms):
    original_key = kms.rpc("CreateKey", {
        "Description": "Original key for update-alias test"
    })["KeyMetadata"]
    replacement_key = kms.rpc("CreateKey", {
        "Description": "Replacement key for update-alias test"
    })["KeyMetadata"]

    original_key_id = original_key["KeyId"]
    replacement_key_id = replacement_key["KeyId"]
    assert original_key_id != replacement_key_id

    alias_name = f"alias/update-alias-{original_key_id}"
    kms.rpc("CreateAlias", {
        "AliasName": alias_name,
        "TargetKeyId": original_key_id,
    })

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    alias_before = next(
        alias_entry
        for alias_entry in aliases_before
        if alias_entry["AliasName"] == alias_name
    )
    assert alias_before["TargetKeyId"] == original_key_id

    result = cli(
        "kms",
        "update-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        replacement_key_id,
    )

    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    alias_after = next(
        alias_entry
        for alias_entry in aliases_after
        if alias_entry["AliasName"] == alias_name
    )
    assert alias_after["TargetKeyId"] == replacement_key_id