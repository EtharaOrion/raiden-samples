def test_update_alias_reassociates_existing_alias(cli, kms):
    first_key = kms.rpc(
        "CreateKey",
        {"Description": "Initial target for update-alias test"},
    )["KeyMetadata"]
    second_key = kms.rpc(
        "CreateKey",
        {"Description": "New target for update-alias test"},
    )["KeyMetadata"]

    alias_name = "alias/update-alias-" + first_key["KeyId"]
    kms.rpc(
        "CreateAlias",
        {"AliasName": alias_name, "TargetKeyId": first_key["KeyId"]},
    )

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    initial_alias = next(
        alias_entry
        for alias_entry in aliases_before
        if alias_entry["AliasName"] == alias_name
    )
    assert initial_alias["TargetKeyId"] == first_key["KeyId"]

    result = cli(
        "kms",
        "update-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        second_key["KeyId"],
    )
    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    updated_alias = next(
        alias_entry
        for alias_entry in aliases_after
        if alias_entry["AliasName"] == alias_name
    )
    assert updated_alias["TargetKeyId"] == second_key["KeyId"]

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})["KeyMetadata"]
    assert described["KeyId"] == second_key["KeyId"]