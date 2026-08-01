def test_delete_alias_rejects_unknown_flag(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "delete-alias invalid-args test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/delete-alias-invalid-args-{key_id}"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli(
        "kms",
        "delete-alias",
        "--alias-name",
        alias_name,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias["AliasName"] == alias_name and alias.get("TargetKeyId") == key_id
        for alias in aliases
    )