def test_update_alias_rejects_unknown_flag_without_changing_target(cli, kms):
    import uuid

    original_key = kms.rpc("CreateKey", {
        "Description": "original alias target",
    })["KeyMetadata"]
    replacement_key = kms.rpc("CreateKey", {
        "Description": "replacement alias target",
    })["KeyMetadata"]
    assert original_key["KeyId"] != replacement_key["KeyId"]

    alias_name = f"alias/update-alias-invalid-args-{uuid.uuid4().hex}"
    kms.rpc("CreateAlias", {
        "AliasName": alias_name,
        "TargetKeyId": original_key["KeyId"],
    })

    result = cli(
        "kms",
        "update-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        replacement_key["KeyId"],
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    matching_aliases = [
        alias for alias in aliases if alias["AliasName"] == alias_name
    ]
    assert len(matching_aliases) == 1
    assert matching_aliases[0]["TargetKeyId"] == original_key["KeyId"]