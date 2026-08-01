def test_create_alias_maximum_length(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "create-alias edge test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/" + ("x" * 250)

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        key_id,
    )

    assert result.returncode == 0
    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias["AliasName"] == alias_name and alias.get("TargetKeyId") == key_id
        for alias in aliases
    )