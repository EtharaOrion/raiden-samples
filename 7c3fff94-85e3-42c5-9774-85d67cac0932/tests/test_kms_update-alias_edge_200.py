def test_update_alias_maximum_length_retargets_existing_alias(cli, kms):
    alias_name = "alias/" + ("x" * 250)

    original_key = kms.rpc("CreateKey", {"Description": "original alias target"})
    replacement_key = kms.rpc("CreateKey", {"Description": "replacement alias target"})
    original_key_id = original_key["KeyMetadata"]["KeyId"]
    replacement_key_id = replacement_key["KeyMetadata"]["KeyId"]
    assert original_key_id != replacement_key_id

    kms.rpc(
        "CreateAlias",
        {
            "AliasName": alias_name,
            "TargetKeyId": original_key_id,
        },
    )

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    matching_before = [
        alias_entry
        for alias_entry in aliases_before
        if alias_entry["AliasName"] == alias_name
    ]
    assert len(matching_before) == 1
    assert matching_before[0]["TargetKeyId"] == original_key_id

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
    matching_after = [
        alias_entry
        for alias_entry in aliases_after
        if alias_entry["AliasName"] == alias_name
    ]
    assert len(matching_after) == 1
    assert matching_after[0]["TargetKeyId"] == replacement_key_id

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})
    assert described["KeyMetadata"]["KeyId"] == replacement_key_id