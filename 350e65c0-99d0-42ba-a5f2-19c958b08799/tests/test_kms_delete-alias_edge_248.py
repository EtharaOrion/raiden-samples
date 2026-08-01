def test_delete_alias_long_name_removes_alias(cli, kms):
    key_id = kms.rpc("CreateKey", {})["KeyMetadata"]["KeyId"]
    alias_name = "alias/" + ("x" * 250)
    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert any(a["AliasName"] == alias_name for a in aliases_before)

    result = cli("kms", "delete-alias", "--alias-name", alias_name)
    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert not any(a["AliasName"] == alias_name for a in aliases_after)