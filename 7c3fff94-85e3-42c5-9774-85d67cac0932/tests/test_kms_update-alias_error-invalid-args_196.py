def test_update_alias_missing_alias_name_rejected_without_changing_state(cli, kms):
    original_key = kms.rpc(
        "CreateKey",
        {"Description": "Original key for update-alias argument validation"},
    )["KeyMetadata"]
    replacement_key = kms.rpc(
        "CreateKey",
        {"Description": "Replacement key for update-alias argument validation"},
    )["KeyMetadata"]

    alias_name = f"alias/update-alias-missing-name-{original_key['KeyId']}"
    kms.rpc(
        "CreateAlias",
        {
            "AliasName": alias_name,
            "TargetKeyId": original_key["KeyId"],
        },
    )

    result = cli(
        "kms",
        "update-alias",
        "--target-key-id",
        replacement_key["KeyId"],
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--alias-name" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    matching_aliases = [
        alias for alias in aliases if alias["AliasName"] == alias_name
    ]
    assert len(matching_aliases) == 1
    assert matching_aliases[0]["TargetKeyId"] == original_key["KeyId"]