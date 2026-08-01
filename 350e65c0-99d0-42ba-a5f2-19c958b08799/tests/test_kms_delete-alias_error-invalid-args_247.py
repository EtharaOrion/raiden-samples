def test_delete_alias_invalid_args(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/test-invalid-flag-alias"
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli(
        "kms", "delete-alias",
        "--alias-name", alias_name,
        "--not-a-real-flag", "x",
    )

    assert result.returncode != 0
    assert "Unknown options" in result.stderr or "not-a-real-flag" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(a["AliasName"] == alias_name for a in aliases)